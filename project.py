from init_database import *
import sys
import os
from pathlib import Path
import csv

load_order = ("User", "Organizer", "Participant", "Administrator","Event",
            "Slot", "Venue", "OnCampus", "OffCampus", "Hosting", "Approval")

def manual_load(cs:mc.cursor, path: Path, filename: str):
    try:
        with open(path/filename, 'r') as file:
            table_name = Path(filename).stem
            csv_reader = csv.reader(file)
            data_to_insert = []
            for row in csv_reader:
                cleaned_row = []
                for cell in row:
                    cleaned_cell = cell.strip()
                    if cleaned_cell.upper() == 'NULL':
                        cleaned_row.append(None)
                    else:
                        cleaned_row.append(cleaned_cell)
                data_to_insert.append(cleaned_row)

            num_columns = len(data_to_insert[0])
            placeholders = ", ".join(["%s"] * num_columns)
            insert_query = f"INSERT INTO {table_name} VALUES ({placeholders})"
            cs.executemany(insert_query, data_to_insert)
    except Exception as e:
        raise Exception(str(data_to_insert)+insert_query+str(e))

def loadnew(cs: mc.cursor, pathstr: str):
    try:
        init(cs)
        path = Path(pathstr)
        for table_name in load_order:
            manual_load(cs, path, table_name+'.csv')
            # table_name = Path(filename).stem
            # cs.execute(f"""LOAD DATA INFILE %s
            #                 INTO TABLE {table_name}
            #                 FIELDS TERMINATED BY ',' 
            #                 LINES TERMINATED BY '\\n'
            #                 IGNORE 1 ROWS;""",
            #                 (str(path/filename),))
        return 1, None

    except Exception as e:
        return 0, table_name+str(e)

def insertAdmin(cs: mc.cursor, uid: int, email: str, username: str,
                joined: str, firstname: str, lastname: str):

    try:
        cs.execute("""INSERT INTO User (uid, email, username, joined)
                        VALUES (%s,%s,%s,%s);""",
                        (uid, email, username, joined))
        cs.execute("""INSERT INTO Administrator (uid, firstname, lastname) 
                VALUES (%s,%s,%s);""",
                (uid, firstname, lastname))
        return 1, None

    except Exception as e:
        return 0, str(e)

def addVenue(cs: mc.cursor, eid:int, vid:int, is_primary:bool):
    try:
        boo = 0
        if is_primary:
            boo = 1
            cs.execute("""SELECT vid
                       FROM Hosting AS h
                       Where h.eid = %s AND is_primary = 1;""",
                       (eid,))
            if cs.fetchone():
                return 0, "Has other primary venue!"

        
        cs.execute("""INSERT INTO Hosting
                   (eid, vid, is_primary)
                   VALUES (%s, %s, %s);""",
                   (eid, vid, boo))
        return 1, None
        
    except Exception as e:
        return 0, str(e)

def reserveSlot(cs: mc.cursor, eid: int, snum: int, uid: int):
    try:
        cs.execute("""UPDATE Slot
                   SET uid = %s, is_reserved = 1
                   WHERE eid = %s AND snum = %s AND is_reserved = 0;""",
                   (uid, eid, snum))
        if cs.rowcount > 0:
            return 1, None
        else:
            return 0, "Already reserved!"
        
    except Exception as e:
        return 0, str(e)
    
def cancelReservation(cs: mc.cursor, eid: int, snum: int, uid: int):
    try:
        cs.execute("""UPDATE Slot
                   SET uid = NULL, is_reserved = 0
                   WHERE eid = %s AND snum = %s AND uid = %s AND is_reserved = 1;""",
                   (eid, snum, uid))
        if cs.rowcount > 0:
            return 1, None
        else:
            return 0, "Previously Unreserved!"
        
    except Exception as e:
        return 0, str(e)

def updateEvent(cs: mc.cursor, eid: int, title: str, datetime: str):
    try:
        cs.execute("""UPDATE Event
                   SET title= %s, datetime = %s
                   WHERE eid = %s;""",
                   (title, datetime, eid))
        if cs.rowcount > 0:
            return 1, None
        else:
            return 0, "Event DNE!"
        
    except Exception as e:
        return 0, str(e)

def deleteOrganizer(cs: mc.cursor, uid: int):
    try:
        cs.execute("""DELETE FROM Organizer
                   WHERE uid = %s;""",
                   (uid,))
        if cs.rowcount > 0:
            return 1, None
        else:
            return 0, "Organizer DNE!"
        
    except Exception as e:
        return 0, str(e)
    
def availableEvents(cs: mc.cursor, date: str):
    try:
        cs.execute("""SELECT e.eid, e.title, e.type, e.datetime, COUNT(s.snum)
                   FROM Event AS e
                   JOIN Slot AS s ON s.eid = e.eid
                   WHERE e.datetime > %s AND s.is_reserved = 0
                   GROUP BY e.eid
                   HAVING COUNT(s.snum) > 0
                   ORDER BY e.datetime ASC, e.eid ASC;""",
                   (date,))
        output = cs.fetchall()
        return 1, output
        
    except Exception as e:
        return 0, str(e)
    
def popularEventTypes(cs: mc.cursor, N: int):
    try:
        cs.execute("""SELECT e.type, SUM(IF(s.is_reserved = 1, 1, 0)) AS num_reserved
                   FROM Event AS e
                   JOIN Slot AS s ON s.eid = e.eid
                   GROUP BY e.type
                   HAVING num_reserved >= %s
                   ORDER BY num_reserved DESC, e.type ASC;""",
                   (N,))
        output = cs.fetchall()
        return 1, output
        
    except Exception as e:
        return 0, str(e)
    
def participantSchedule(cs: mc.cursor, uid: int):
    try:
        cs.execute("""SELECT selected_e.eid, title, type, datetime, snum, v.vid, street, city, state, zip
                   FROM Venue AS v
                   LEFT JOIN Hosting AS h ON v.vid = h.vid AND h.is_primary = 1
                   RIGHT JOIN (SELECT e.eid, title, type, datetime, snum
                        FROM Event AS e
                        JOIN Slot AS s ON e.eid = s.eid
                        WHERE s.uid = %s
                        ) AS selected_e ON h.eid = selected_e.eid
                   ORDER BY datetime ASC;""",
                   (uid,))
        output = cs.fetchall()
        return 1, output
        
    except Exception as e:
        return 0, str(e)
    
def organizerStats(cs: mc.cursor, N: int):
    try:
        cs.execute("""SELECT o.uid, username, department, COUNT(e.eid)
                   FROM Organizer AS o 
                   JOIN User AS u ON o.uid = u.uid
                   LEFT JOIN Event AS e ON o.uid = e.creator_uid
                   GROUP BY o.uid
                   HAVING COUNT(e.eid) >= %s
                   ORDER BY o.uid ASC;""",
                   (N,))
        output = cs.fetchall()
        return 1, output
        
    except Exception as e:
        return 0, str(e)
    
def venueEvents(cs: mc.cursor, vid: int):
    try:
        cs.execute("""SELECT e.eid, title, type, datetime, is_primary
                   FROM Event AS e
                   JOIN Hosting AS h ON e.eid = h.eid
                   WHERE h.vid = %s
                   ORDER BY datetime ASC, e.eid ASC;""",
                   (vid,))
        output = cs.fetchall()
        return 1, output
        
    except Exception as e:
        return 0, str(e)

FuncList = {'import': loadnew,
            'insertAdmin': insertAdmin,
            'addVenue': addVenue,
            'reserveSlot': reserveSlot,
            'cancelReservation': cancelReservation,
            'updateEvent': updateEvent,
            'deleteOrganizer': deleteOrganizer,
            'availableEvents': availableEvents,
            'popularEventTypes': popularEventTypes,
            'participantSchedule': participantSchedule,
            'organizerStats': organizerStats,
            'venueEvents': venueEvents}


def main():
    conn = mc.connect(host='localhost', user='test', password='password', database='cs122a', allow_local_infile=True, use_pure=True)
    cursor = conn.cursor()
    try:
        # cursor.execute("SET GLOBAL local_infile=1;")
        result = FuncList[sys.argv[1]](cursor, *sys.argv[2:])
        content = result[1]
        if not result[0]:
            conn.rollback()
            print("Fail")
        elif not content:
            conn.commit()
            print('Success')
        else:
            content = [['NULL' if item is None else item for item in row] for row in content]
            for tup in content:
                print(*tup, sep=',')

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
