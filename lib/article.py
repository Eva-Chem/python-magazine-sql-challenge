from .database_utils import get_connection

class Article:
    def __init__(self, id=None, title=None, content=None, author_id=None, magazine_id=None):
        self.id = id
        self.title = title
        self.content = content
        self.author_id = author_id
        self.magazine_id = magazine_id

    @classmethod
    def new_from_db(cls, row):
        return cls(id=row[0], title=row[1], content=row[2], author_id=row[3], magazine_id=row[4])

    @classmethod
    def find_by_id(cls, id):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM articles WHERE id = ?", (id,))
        row = cursor.fetchone()
        connection.close()
        return cls.new_from_db(row) if row else None

    def save(self):
        connection = get_connection()
        cursor = connection.cursor()

        if self.id:
            cursor.execute("""
                UPDATE articles
                SET title = ?, content = ?, author_id = ?, magazine_id = ?
                WHERE id = ?
            """, (self.title, self.content, self.author_id, self.magazine_id, self.id))
        else:
            cursor.execute("""
                INSERT INTO articles (title, content, author_id, magazine_id)
                VALUES (?, ?, ?, ?)
            """, (self.title, self.content, self.author_id, self.magazine_id))
            self.id = cursor.lastrowid

        connection.commit()
        connection.close()
