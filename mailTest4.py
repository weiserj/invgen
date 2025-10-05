import imaplib
import imapclient
from email.message import EmailMessage

# List der Mailboxen ermitteln
def listMailboxes(m):
    print("\nListe aller Mailboxen:")
    l = m.list()
    mailboxList = l[1]
    for l2 in mailboxList:
        print(l2)
    print("*** ENDE ***\n")

def deleteMailboxes(m):
    """
    Wird im Moment nicht verwendet, da waren kleine Unklarheiten beim Mail-Server
    :type m: object
    """
    m.select("EEGs.Reidlinger")
    m.unsubscribe("EEGs.Reidlinger")
    m.delete(mailbox="EEGs.Reidlinger")
    #m.unselect()
    m.select(mailbox="Drafts.EEGs.Reidlinger")
    m.unsubscribe("Drafts.EEGs.Reidlinger")
    m.delete(mailbox="Drafts.EEGs.Reidlinger")
    m.select(mailbox="Drafts.EEGs")
    m.delete(mailbox="Drafts.EEGs")
    pass


# Erzeugen einer Test-Email
def createMail(mailboxName):
    msg1 = EmailMessage()
    msg1['Subject'] = f'Hallo, hallo message 27.11, 10:57! Created for {mailboxName}'
    msg1['From'] = 'johann.weiser@aon.at'
    msg1['To'] = 'johannp.weiser@gmail.com, johann.weiser@aon.at'

    msg1.set_content('Hi there,\n this is a test E-mail from Python!!!!!\n'
                     'bisher war date_time=None, nun date_time=" " \n'
                     ' das funktioniert nicht, jetzt probiere ich date_time=""')

    filename = 'reidlinger_markus.pdf'
    with open('./results/' + filename, 'rb') as content_file:
        content = content_file.read()
        msg1.add_attachment(content, maintype='application/pdf', subtype='pdf', filename=filename)

    return msg1
    pass


# Erzeugen einer Mailbox und Einspielen einer Mail
def createMailbox(m):
    mailboxName="Drafts.EEGs"
    # unklar, was a und b zurückliefern
    a = m.create(mailboxName) # bringt nichts!!!
    b = m.subscribe(mailboxName)
    print(a,b)
    listMailboxes(m)
    # Liste der subscribed Mailboxe
    x = m.lsub()

    # select mailbox
    y=m.select(mailbox=mailboxName)

    # hier wird die Mail erzeugt
    ms = createMail()

    # undhier wird sie in die Mailbox eingespielt
    x = m.append(mailbox=mailboxName, flags ="", date_time="", message=ms.as_bytes() )
    # m.append(mailbox="Drafts", flags="\\Drafts", date_time=None, message=ms.as_bytes())
    pass


def registerMail(m, mailboxName):
    b = m.subscribe(mailboxName)
    y = m.select(mailbox=mailboxName)
    ms = createMail(mailboxName) # Der Mailboxnamewird im Subject hinzugefügt!!
    x = m.append(mailbox=mailboxName, flags ="(\\Draft)", date_time="", message=ms.as_bytes() )
    #x = m.append(mailbox=mailboxName, flags=None, date_time="", message=ms.as_bytes() )
    z=m.status(mailboxName, "(MESSAGES UIDVALIDITY UIDNEXT)")
    x = m.list(mailboxName)
    print(x)
    print(z)
    # nun wird versucht das \\Draft Flag zu setzen
    # das geht auch nicht!!
    #u = m.store(1, '+FLAGS', '\\Drafts')
    pass


def setDraftFlag(m, mailboxName):
    y = m.select(mailbox=mailboxName)
    u = m.store('1', '+FLAGS', '(\\Drafts)')
    pass


def listSingleMailbox(m, mailbox):
    m.list(mailbox)
    m.select(mailbox)
    print(f'\nListing of Mailbox "{mailbox}":')
    x = m.fetch('1:*', "(UID INTERNALDATE FLAGS BODY[HEADER.fields (subject)])")
    for y in x[1]:
        print(y)

# begin of main method
M=imaplib.IMAP4("securemail.a1.net")
M.login('johann.weiser@aon.at', 'password')
# x = M.select()
# y = M.select(mailbox="github")

# das ist so ein kleines Löschprogramm!
# es leibt nur das List-Programm, das delete wird Kommentar!!
listMailboxes(M)
# deleteMailboxes(M)
# jetzt wirdangenommen, dass die mailbox schon eingerichtet ist!!
# createMailbox(M)
M.list("EEGs")
M.select("EEGs")
#M.fetch("(0:3, 4:*)", "(RFC822.HEADER, FLAGS INTERNALDATE)")

# 1:* geht nicht, wenndie mailbox leer ist
#x=M.fetch("1:*", "(RFC822.HEADER FLAGS INTERNALDATE uid)")
# die folgende Zeile funktiert!!!!

# 1:* geht nicht, wenndie mailbox leer ist
#M.fetch('1:*', "(UID INTERNALDATE BODY[HEADER])")
# das passt jetzt auch!!!

# 1:* geht nicht, wenndie mailbox leer ist
#x=M.fetch('1:*', "(UID INTERNALDATE BODY[HEADER.fields (subject)])")

#for y in x[1]:
#    print(y)
pass

registerMail(M, "EEGs") # da gehts nicht mit Drafts Flag
registerMail(M, "Drafts.EEGs")
# hier im \\Drafts Ordner sollte es gehen
registerMail(M, "Drafts")

listSingleMailbox(M, "Drafts")
#imaplib.IMAP4.debug=4
#setDraftFlag(M, "EEGs")

# Schließt die im Moment ausgewöhlte (selected) Mailbox
# close ist erlaubt, wenn eine mailbox selektiert ist!
M.close()
M.logout()