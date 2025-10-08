from .database_utils import get_connection
from .article import Article
from .magazine import Magazine


class Author:
    def __init__(self, name):
        if not isinstance(name, str) or len(name.strip()) == 0:
            raise ValueError("Author name must be a non-empty string.")
        self._name = name
        self.id = None

    @property
    def name(self):
        return self._name

    @classmethod
    def new_from_db(cls, row):
        author = cls(row[1])
        author.id = row[0]
        return author

    @classmethod
    def find_by_id(cls, id):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM authors WHERE id = ?", (id,))
        row = cursor.fetchone()
        connection.close()
        return cls.new_from_db(row) if row else None

    def save(self):
        connection = get_connection()
        cursor = connection.cursor()

        if self.id is None:
            cursor.execute("INSERT INTO authors (name) VALUES (?)", (self._name,))
            self.id = cursor.lastrowid
        else:
            cursor.execute("UPDATE authors SET name = ? WHERE id = ?", (self._name, self.id))

        connection.commit()
        connection.close()

    def articles(self):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM articles WHERE author_id = ?", (self.id,))
        rows = cursor.fetchall()
        connection.close()
        return [Article.new_from_db(row) for row in rows]

    def magazines(self):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT DISTINCT m.*
            FROM magazines m
            JOIN articles a ON m.id = a.magazine_id
            WHERE a.author_id = ?
        """, (self.id,))
        rows = cursor.fetchall()
        connection.close()
        return [Magazine.new_from_db(row) for row in rows]
    
    def add_article(self, magazine, title):
        from .article import Article
        article = Article(title, self, magazine)
        article.save()
        return article

    def topic_areas(self):
        magazines = self.magazines()
        return list({mag.category for mag in magazines})
