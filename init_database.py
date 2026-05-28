import mysql.connector as mc
def init(cs: mc.cursor):
    cs.execute("DROP TABLE IF EXISTS User")
    cs.execute("DROP TABLE IF EXISTS Organizer")
    cs.execute("DROP TABLE IF EXISTS Participant")
    cs.execute("DROP TABLE IF EXISTS Administrator")
    cs.execute("DROP TABLE IF EXISTS Event")
    cs.execute("DROP TABLE IF EXISTS Slot")
    cs.execute("DROP TABLE IF EXISTS Venue")
    cs.execute("DROP TABLE IF EXISTS OnCampus")
    cs.execute("DROP TABLE IF EXISTS OffCampus")
    cs.execute("DROP TABLE IF EXISTS Hosting")
    cs.execute("DROP TABLE IF EXISTS Approval")
    cs.execute("DROP TABLE IF EXISTS Event")

    cs.execute("""CREATE TABLE User (
                uid INT,
                email TEXT NOT NULL,
                username TEXT NOT NULL,
                joined DATE NOT NULL,
                PRIMARY KEY (uid)
            );""")

    cs.execute("""CREATE TABLE Organizer (
                    uid INT,
                    department TEXT NOT NULL,
                    experience INT NOT NULL,
                    PRIMARY KEY (uid),
                    FOREIGN KEY (uid) REFERENCES User(uid) ON DELETE CASCADE
                );""")

    cs.execute("""CREATE TABLE Participant (
                uid INT,
                type TEXT,
                PRIMARY KEY (uid),
                FOREIGN KEY (uid) REFERENCES User(uid) ON DELETE CASCADE
            );""")

    cs.execute("""CREATE TABLE Administrator (
        uid INT,
        firstname TEXT NOT NULL,
        lastname TEXT NOT NULL,
        PRIMARY KEY (uid),
        FOREIGN KEY (uid) REFERENCES User(uid) ON DELETE CASCADE
    );""")

    cs.execute("""CREATE TABLE Event (
                    eid INT,
                    creator_uid INT NOT NULL,
                    title TEXT NOT NULL,
                    type TEXT NOT NULL,
                    datetime DATETIME NOT NULL,
                    PRIMARY KEY (eid),
                    FOREIGN KEY (creator_uid) REFERENCES Organizer(uid) ON DELETE CASCADE
                );""")
    
    cs.execute("""CREATE TABLE Slot (
                eid INT,
                snum INT NOT NULL,
                is_reserved BOOLEAN NOT NULL,
                uid INT,
                PRIMARY KEY (eid, snum),
                FOREIGN KEY (eid) REFERENCES Event(eid) ON DELETE CASCADE,
                FOREIGN KEY (uid) REFERENCES Participant(uid) ON DELETE CASCADE
            );""")
    
    cs.execute("""CREATE TABLE Venue (
                    vid INT,
                    street TEXT NOT NULL,
                    city TEXT NOT NULL,
                    state TEXT NOT NULL,
                    zip TEXT NOT NULL,
                    PRIMARY KEY (vid)
                );""")
    
    cs.execute("""CREATE TABLE OnCampus (
                    vid INT,
                    code TEXT NOT NULL,
                    PRIMARY KEY (vid),
                    FOREIGN KEY (vid) REFERENCES Venue(vid) ON DELETE CASCADE
                );""")
    
    cs.execute("""CREATE TABLE OffCampus (
                vid INT,
                distance INT NOT NULL,
                PRIMARY KEY (vid),
                FOREIGN KEY (vid) REFERENCES Venue(vid) ON DELETE CASCADE
            );""")
    
    cs.execute("""CREATE TABLE Hosting (
                eid INT NOT NULL,
                vid INT NOT NULL,
                is_primary BOOLEAN NOT NULL,
                PRIMARY KEY (eid, vid),
                FOREIGN KEY (eid) REFERENCES Event(eid) ON DELETE CASCADE,
                FOREIGN KEY (vid) REFERENCES Venue(vid) ON DELETE CASCADE
            );""")
    
    cs.execute("""CREATE TABLE Approval (
                uid INT NOT NULL,
                vid INT NOT NULL,
                valid_from DATE NOT NULL,
                valid_until DATE NOT NULL,
                PRIMARY KEY (uid, vid),
                FOREIGN KEY (uid) REFERENCES Administrator(uid) ON DELETE CASCADE,
                FOREIGN KEY (vid) REFERENCES OffCampus(vid) ON DELETE CASCADE
            );""")
    

