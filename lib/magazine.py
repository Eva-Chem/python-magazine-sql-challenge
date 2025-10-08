from .database_utils import get_connection
from .article import Article
from .author import Author


class Magazine:
    def __init__(self, name, category):
        if not isinstance(name, str) or len(name.strip()) == 0:
            raise ValueError("Magazine name must be a non-empty string.")
        if not isinstance(category, str) or len(category.strip()) == 0:
            raise ValueError("Magazine category must be a non-empty string.")
        self._name = name
        self._category = category
        self.id = None

    # --- Properties ---
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str) or len(value.strip()) == 0:
            raise ValueError("Magazine name must be a non-empty string.")
        self._name = value

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, value):
        if not isinstance(value, str) or len(value.strip()) == 0:
            raise ValueError("Magazine category must be a non-empty string.")
        self._category = value

    # --- Database Utility Methods ---
    @classmethod
    def new_from_db(cls, row):
        magazine = cls(row[1], row[2])
        magazine.id = row[0]
        return magazine

    @classmethod
    def find_by_id(cls, id):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM magazines WHERE id = ?", (id,))
        row = cursor.fetchone()
        connection.close()
        return cls.new_from_db(row) if row else None

    def save(self):
        connection = get_connection()
        cursor = connection.cursor()
        if self.id is None:
            cursor.execute(
                "INSERT INTO magazines (name, category) VALUES (?, ?)",
                (self._name, self._category)
            )
            self.id = cursor.lastrowid
        else:
            cursor.execute(
                "UPDATE magazines SET name = ?, category = ? WHERE id = ?",
                (self._name, self._category, self.id)
            )
        connection.commit()
        connection.close()

    # --- Relationships ---
    def articles(self):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM articles WHERE magazine_id = ?", (self.id,))
        rows = cursor.fetchall()
        connection.close()
        return [Article.new_from_db(row) for row in rows]

    def contributors(self):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT DISTINCT a.*
            FROM authors a
            JOIN articles ar ON a.id = ar.author_id
            WHERE ar.magazine_id = ?
        """, (self.id,))
        rows = cursor.fetchall()
        connection.close()
        return [Author.new_from_db(row) for row in rows]
    
    def article_titles(self):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT title FROM articles WHERE magazine_id = ?", (self.id,))
        rows = cursor.fetchall()
        connection.close()
        return [row[0] for row in rows]

    def contributing_authors(self):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT author_id
            FROM articles
            WHERE magazine_id = ?
            GROUP BY author_id
            HAVING COUNT(id) > 2
        """, (self.id,))
        author_ids = [row[0] for row in cursor.fetchall()]
        connection.close()

        from .author import Author
        return [Author.find_by_id(aid) for aid in author_ids]

    @classmethod
    def top_publisher(cls):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT magazine_id, COUNT(id) as article_count
            FROM articles
            GROUP BY magazine_id
            ORDER BY article_count DESC
            LIMIT 1
        """)
        row = cursor.fetchone()
        connection.close()
        if row:
            return cls.find_by_id(row[0])
        return None
