import json
import random

tech_topics = ["React", "Python", "FastAPI", "Docker", "AWS", "Kubernetes", "Angular", "Vue", "CSS", "SQL", "Mongo",
               "Node", "Go", "Rust", "TypeScript", "Linux", "DevOps", "Security"]
adjectives = ["Mastering", "Advanced", "Practical", "Modern", "High-Performance", "Effective", "Learning", "Pro",
              "Architecting", "Deep Dive into"]
types = ["Development", "Engineering", "Architecture", "Patterns", "in Action", "Secrets", "Cookbook", "Fundamentals",
         "Handbook", "Masterclass"]

first_names = ["John", "Sarah", "Alex", "David", "Emma", "Michael", "Rachel", "Chris", "Jessica", "Jatin"]
last_names = ["Smith", "Doe", "Johnson", "Davis", "Chen", "Patel", "Kim", "O'Connor", "Gulati", "Jenkins"]

# Comprehensive topic-specific image pools so covers always match the title
topic_covers = {
    "React": [
        "https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=600&q=80",
        "https://images.unsplash.com/photo-1581291518633-83b4ebd1d83e?w=600&q=80",
        "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&q=80"
    ],
    "Python": [
        "https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=600&q=80",
        "https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=600&q=80",
        "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=600&q=80"
    ],
    "FastAPI": [
        "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&q=80",
        "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=600&q=80",
        "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=600&q=80"
    ],
    "Docker": [
        "https://images.unsplash.com/photo-1605745341119-8fdd7062e0f8?w=600&q=80",
        "https://images.unsplash.com/photo-1618401471353-b98aedd04e11?w=600&q=80",
        "https://images.unsplash.com/photo-1518770660439-4636190af475?w=600&q=80"
    ],
    "AWS": [
        "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=600&q=80",
        "https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=600&q=80",
        "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=600&q=80"
    ],
    "Kubernetes": [
        "https://images.unsplash.com/photo-1618401471353-b98aedd04e11?w=600&q=80",
        "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=600&q=80",
        "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=600&q=80"
    ],
    "Angular": [
        "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=600&q=80",
        "https://images.unsplash.com/photo-1531403009284-440f080d1e12?w=600&q=80",
        "https://images.unsplash.com/photo-1581291518633-83b4ebd1d83e?w=600&q=80"
    ],
    "Vue": [
        "https://images.unsplash.com/photo-1579403124614-197f69d8187b?w=600&q=80",
        "https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?w=600&q=80",
        "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&q=80"
    ],
    "CSS": [
        "https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?w=600&q=80",
        "https://images.unsplash.com/photo-1542838132-92c53300491e?w=600&q=80",
        "https://images.unsplash.com/photo-1581291518633-83b4ebd1d83e?w=600&q=80"
    ],
    "SQL": [
        "https://images.unsplash.com/photo-1544383835-bda2bc66a55d?w=600&q=80",
        "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=600&q=80",
        "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=600&q=80"
    ],
    "Mongo": [
        "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=600&q=80",
        "https://images.unsplash.com/photo-1544383835-bda2bc66a55d?w=600&q=80",
        "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=600&q=80"
    ],
    "Node": [
        "https://images.unsplash.com/photo-1629654297299-c8506221ca97?w=600&q=80",
        "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=600&q=80",
        "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&q=80"
    ],
    "Go": [
        "https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=600&q=80",
        "https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=600&q=80",
        "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=600&q=80"
    ],
    "Rust": [
        "https://images.unsplash.com/photo-1518770660439-4636190af475?w=600&q=80",
        "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&q=80",
        "https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=600&q=80"
    ],
    "TypeScript": [
        "https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=600&q=80",
        "https://images.unsplash.com/photo-1581291518633-83b4ebd1d83e?w=600&q=80",
        "https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=600&q=80"
    ],
    "Linux": [
        "https://images.unsplash.com/photo-1629654297299-c8506221ca97?w=600&q=80",
        "https://images.unsplash.com/photo-1531403009284-440f080d1e12?w=600&q=80",
        "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=600&q=80"
    ],
    "DevOps": [
        "https://images.unsplash.com/photo-1618401471353-b98aedd04e11?w=600&q=80",
        "https://images.unsplash.com/photo-1605745341119-8fdd7062e0f8?w=600&q=80",
        "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=600&q=80"
    ],
    "Security": [
        "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=600&q=80",
        "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=600&q=80",
        "https://images.unsplash.com/photo-1614064641938-3bbee52942c7?w=600&q=80"
    ],
}

books = []

for i in range(1500):
    topic = random.choice(tech_topics)
    title = f"{random.choice(adjectives)} {topic} {random.choice(types)}"
    author = f"{random.choice(first_names)} {random.choice(last_names)}"

    desc_topic = random.choice(tech_topics)
    description = (
        f"This authoritative volume explores the core fundamentals and advanced engineering paradigms behind {topic}. "
        f"Designed for senior software architects and modern developers, it delivers deep structural insights into integrating "
        f"{topic} with high-throughput workflows like {desc_topic}. Readers will discover production-grade design patterns, "
        f"performance optimization techniques, memory management strategies, and robust troubleshooting methodologies "
        f"tailored to scale seamlessly in enterprise cloud ecosystems."
    )

    total = random.randint(5, 100)
    available = random.randint(0, total)
    price = round(random.uniform(25.0, 95.0), 2)

    # Strictly pull images matching the exact topic of the book title
    images = topic_covers.get(topic, topic_covers["Python"])

    books.append({
        "title": title,
        "author": author,
        "description": description,
        "available_copies": available,
        "total_copies": total,
        "price": price,
        "images": images
    })

with open('bulk_books.json', 'w', encoding='utf-8') as f:
    json.dump(books, f, indent=2)

print(f"Successfully generated {len(books)} books with strictly matched topic covers!")