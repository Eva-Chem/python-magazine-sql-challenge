from lib.database_utils import create_tables
from lib.author import Author
from lib.magazine import Magazine
from lib.article import Article

# Create the database tables
create_tables()

# --- Sample testing section ---
print("✅ Database tables created successfully!")

# Create a new author
author = Author("Eva Chemutai")
author.save()

# Create a new magazine
mag = Magazine("Tech Monthly", "Technology")
mag.save()

# Create a new article
article = Article("AI Revolution", author, mag)
article.save()

print("✅ Sample data inserted successfully!")

# Fetch data back
print("\nAuthors in DB:")
print(Author.find_by_id(author.id).__dict__)

print("\nMagazines in DB:")
print(Magazine.find_by_id(mag.id).__dict__)

print("\nArticles in DB:")
print(Article.find_by_id(article.id).__dict__)
