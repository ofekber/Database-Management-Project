# Contents Website — Database Management Project

A Django web application for managing movies, actors, users, and viewing records. The app provides a Netflix-style interface to run analytics queries, add actors to movies, and record when users watch movies.

## Features

- **Query Results** — View three analytics reports:
  - Genre statistics: movie count and average rating per genre (from top 20 movies by revenue)
  - Actor statistics: actors not in any user’s favorites who appear in 3+ “improving” movies, with movie counts
  - “Fake fans” per country: users who watch more than the country average but have never watched a movie featuring their favorite actor
- **Add Actor to Movie** — Assign an actor to a movie with salary; validates movie existence, no duplicate cast, and remaining budget
- **Record Watching** — Log a user watching a movie on a date with a rating; validates duplicates, chronological order, and that the date is not before the movie’s release

## Data Model

The application uses four main tables:

| Table | Description |
|-------|-------------|
| **Movies** | `title` (PK), `genre`, `releaseDate`, `budget` |
| **ActorsInMovies** | `aName`, `mTitle` (FK → Movies), `salary` — cast and salaries per movie |
| **Users** | `uID` (PK), `country`, `favActor` |
| **Watching** | `uID` (FK → Users), `mTitle` (FK → Movies), `wDate`, `rating` — when a user watched a movie and their rating |

The queries rely on SQL views defined in `Project/view_queries.sql` (e.g. `TOP20`, `ImprovingMovies`, `MoreThanAverageInCountry`, `FakeFans`, `MoreThan5FakeFans`). These views must be created in your database before using the Query Results page.

## Project Structure

```
Database-Management-Project/
├── manage.py                 # Django management script
├── csv files/                # Sample/seed data
│   ├── ActorsInMovies.csv
│   ├── Movies.csv
│   ├── Users.csv
│   └── Watching.csv
└── Project/
    ├── Content_App/          # Main Django app
    │   ├── models.py         # Movies, Users, ActorsInMovies, Watching (unmanaged)
    │   ├── views.py         # Index, QueryResults, AddActortoMovie, RecordWatching
    │   ├── urls.py          # URL routing
    │   └── admin.py
    ├── templates/
    │   ├── index.html       # Home with links to all features
    │   ├── QueryResults.html
    │   ├── AddActorToMovie.html
    │   └── RecordWatching.html
    └── view_queries.sql     # SQL views required for the analytics queries
```

## Setup

1. **Python environment**  
   Use Python 3 with Django installed (e.g. `pip install django`).

2. **Django settings**  
   `manage.py` uses the settings module `Project_B.settings`. Ensure you have a Django project (e.g. `Project_B`) with `Content_App` in `INSTALLED_APPS`, `TEMPLATES` pointing at `Project/templates`, and the app’s `urls.py` included in the root URLconf.

3. **Database**  
   Configure your database in the project’s `settings.py` (e.g. SQL Server for the given SQL dialect). Create the four tables to match the models (or use migrations if you switch to managed models). Run the statements in `Project/view_queries.sql` to create the views used by the Query Results page.

4. **Load data (optional)**  
   Use the CSV files in `csv files/` to populate `Movies`, `Users`, `ActorsInMovies`, and `Watching` if you want sample data.

## Running the Application

From the project root (where `manage.py` is):

```bash
python manage.py runserver
```

Then open the home page (e.g. `http://127.0.0.1:8000/`) and use the links to Query Results, Add Actor to Movie, and Record Watching.

## Routes

| URL | View | Description |
|-----|------|-------------|
| `/`, `/index.html` | `index` | Home page with navigation |
| `/QueryResults.html` | `QueryResults` | Analytics query results (3 tables) |
| `/AddActorToMovie.html` | `AddActortoMovie` | Form to add an actor to a movie |
| `/RecordWatching.html` | `RecordWatching` | Form to record a user watching a movie |

## Technologies

- **Backend:** Django (Python)
- **Database:** SQL (views and raw queries; schema matches SQL Server–style syntax)
- **Frontend:** HTML templates with inline CSS, Netflix-inspired dark theme

## Authors

Shany Yurist and Ofek Bernstein.
