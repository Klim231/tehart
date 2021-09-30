import sqlite3

class Members:
    def __init__(self, path):
        self.conection = sqlite3.connect(path)
        self.cursor = self.conection.cursor()


    def registration(self, user_id, username, mail, phone, city):
        with self.conection:
            id = self.cursor.execute('SELECT id FROM Members').fetchall()
            mass = []
            for i in id:
                i = i[0]
                mass.append(i)
            true_id = max(mass)
            return self.cursor.execute("INSERT INTO Members VALUES(?,?,?,?,?,?)", (true_id+1, user_id, username, mail, phone, city))


    def check_registration(self, user_id):
        with self.conection:

            print(self.cursor.execute('SELECT * FROM Members').fetchall())
            for user in self.cursor.execute('SELECT * FROM Members').fetchall():
                print(user)
                if user_id == user[1]:
                    return True
                else:
                    pass
            return False


    def get_profile(self, user_id):
        with self.conection:
            info = self.cursor.execute(f'SELECT id, user_id, username,mail,phone,city FROM Members WHERE user_id={user_id}').fetchone()
            return info

    def update_phone(self, user_id, phone):
        with self.conection:
            return self.cursor.execute('UPDATE Members SET phone=?  WHERE user_id=?', (phone, user_id))
    def test(self):
        with self.conection:
            id = self.cursor.execute('SELECT id FROM Members').fetchall()
            mass = []
            for i in id:
                i = i[0]
                mass.append(i)
            print(max(mass))
