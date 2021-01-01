GENRE = (
    ('adv', 'adventure'),
    ('ang', 'angst'),
    ('dra', 'drama'),
    ('fri', 'friendship'),
    ('gen', 'general'),
    ('hum', 'humor'),
    ('hur', 'hurt/comfort'),
    ('mys', 'mystery'),
    ('rom', 'romance'),
    ('tra', 'tragedy'),
    ('hor', 'horror'),
    ('fan', 'fantasy')
)

RATING = (
    ('K', 'K'),
    ('K+', 'K+'),
    ('T', 'T'),
    ('M', 'M'),
)

RATING_CHOICES = (
    (0, 'all'),
    (1, 'K'),
    (2, 'K+'),
    (3, 'T'),
    (4, 'M'),
)

GENRES_CHOICES = (
    (0, 'all'),
    ('adv', 'adventure'),
    ('ang', 'angst'),
    ('dra', 'drama'),
    ('fri', 'friendship'),
    ('gen', 'general'),
    ('hum', 'humor'),
    ('hur', 'hurt/comfort'),
    ('mys', 'mystery'),
    ('rom', 'romance'),
    ('tra', 'tragedy'),
    ('hor', 'horror'),
    ('fan', 'fantasy')
)

SORT_CHOICES = (
    (0, "All"),
    (1, "Last updated"),
    (2, "Number of reviews"),
    (3, "Number of followers")
)

LENGTH_CHOICES = (
    (0, "All"),
    (1, "< 1K words"),
    (2, ">10K words"),
    (3, ">40K words"),
    (4, ">60k words"),
    (5, ">100K words")
)

STATUS_CHOICES = (
    (0, "All"),
    (1, "Complete"),
    (2, "In progress"),
)

ISSUES = (
    ("m", "metadata"),
    ("c", "chapters"),
    ("o", "other")
)
