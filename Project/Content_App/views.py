from django.shortcuts import render
from .models import Actorsinmovies, Movies, Users, Watching
from django.db import connection


def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def index(request):
    return render(request, 'index.html')

def QueryResults(request):
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT genre, COUNT(DISTINCT title) AS NumberOfMoviesInGenre, ROUND(AVG(CAST(rating AS FLOAT)),2) AS AverageRating
        FROM TOP20 LEFT JOIN (
            SELECT *
            FROM Watching
        ) AS A ON A.mtitle = TOP20.title
        GROUP BY genre
        ORDER BY NumberOfMoviesInGenre DESC
        """)
        sql_res1 = dictfetchall(cursor)

        cursor.execute("""
        SELECT AIM2.aName, COUNT(mTitle) AS NumberOfMoviesPlayed
        FROM ActorsInMovies AIM2 JOIN (
            SELECT aName
            FROM ImprovingMovies IM JOIN ActorsInMovies AIM ON IM.mTitle = AIM.mTitle
            WHERE aName NOT IN (
                SELECT favActor
                FROM Users
            )
            GROUP BY AIM.aName HAVING COUNT(AIM.mTitle) >= 3
        ) AS A ON A.aName = AIM2.aName
        GROUP BY AIM2.aName
        """)
        sql_res2 = dictfetchall(cursor)


        cursor.execute("""
        SELECT MT5.country,uID
        FROM MoreThan5FakeFans MT5 JOIN FakeFans FF ON MT5.country = FF.country
        JOIN (
        SELECT MT5.country, MAX(WatchingsPerUser) AS MaxWatchingInCountry
        FROM MoreThan5FakeFans MT5 JOIN FakeFans FF ON MT5.country = FF.country
        GROUP BY MT5.country
        ) AS A ON A.country = MT5.country
        WHERE WatchingsPerUser = MaxWatchingInCountry
        ORDER BY MT5.country ASC
        """)

        sql_res3 = dictfetchall(cursor)
    return render(request, 'QueryResults.html',{'sql_res1': sql_res1,'sql_res2': sql_res2, 'sql_res3': sql_res3})


def AddActortoMovie(request):
    error_message = None  # Initialize error message
    success_message = None  # Initialize success message

    if request.method == "POST":
        with connection.cursor() as cursor:
            # Check if the movie exists
            cursor.execute("""
            SELECT title
            FROM Movies
            WHERE title = %s;
            """, [request.POST.get("title")])
            movie = cursor.fetchone()

            if not movie:  # Movie doesn't exist
                error_message = "Error! The movie doesn't exist!"
            else:
                # Movie exists, now check if the actor is already in the movie
                cursor.execute("""
                SELECT aName
                FROM ActorsInMovies
                WHERE aName = %s
                AND mTitle = %s;
                """, [request.POST.get("name"), request.POST.get("title")])
                actor_exists = cursor.fetchone()

                if actor_exists:  # Actor is already in the movie
                    error_message = "Error! The actor already plays in that movie!"
                else:
                    # Actor is not in the movie, check if the salary is within the budget
                    cursor.execute("""
                    SELECT (budget - ISNULL(TotalCost, 0)) AS RemainingBudget
                    FROM Movies LEFT JOIN (
                        SELECT mTitle, SUM(salary) AS TotalCost
                        FROM ActorsInMovies AIM
                        WHERE mTitle = %s
                        GROUP BY mTitle
                    ) AS A ON A.mTitle = Movies.title
                    WHERE Movies.title = %s
                    AND %s <= (budget - ISNULL(TotalCost, 0));
                    """, [request.POST.get('title'), request.POST.get('title'), request.POST.get('salary')])
                    budget_check = cursor.fetchone()

                    if not budget_check:  # Salary exceeds budget
                        error_message = "Error! The actor is asking for too much money!"
                    else:
                        # Everything is fine, add the actor to the movie
                        cursor.execute("""
                        INSERT INTO ActorsInMovies (aName, mTitle, salary)
                        VALUES (%s, %s, %s)
                        """, [request.POST.get('name'), request.POST.get('title'), request.POST.get('salary')])
                        success_message = "Success! The actor has been added to the movie."

    # Fetch latest 5 movies
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT TOP 5 title, genre, releaseDate
        FROM Movies JOIN ActorsInMovies AIM ON Movies.title = AIM.mTitle
        WHERE AIM.aName = %s
        ORDER BY releaseDate DESC 
        """, [request.POST.get('name')])
        latest_movies = dictfetchall(cursor)

    # Return appropriate messages or render template
    context = {
        "error_message": error_message,
        "success_message": success_message,
        "latest_movies": latest_movies,
    }
    return render(request, 'AddActorToMovie.html', context)


def RecordWatching(request):
    success_message = None
    error_message = None

    with connection.cursor() as cursor:
        # Fetch all movies
        cursor.execute("""
        SELECT title
        FROM Movies
        """)
        all_movies = dictfetchall(cursor)

        # Fetch all users
        cursor.execute("""
        SELECT uID
        FROM Users
        """)
        all_users = dictfetchall(cursor)

    if request.method == "POST":
        # Check if the record already exists
        with connection.cursor() as cursor:
            cursor.execute("""
            SELECT uID, mTitle, wDate
            FROM Watching
            WHERE uID = %s
            AND mTitle = %s
            AND wDate = %s
            """, [request.POST.get("id"), request.POST.get("title"), request.POST.get("date")])
            record_already_exists = cursor.fetchone()

            if record_already_exists:
                error_message = "Error! The record entered already exists!"
            else:
                # Check if there's a later watching record for the same user and movie
                cursor.execute("""
                SELECT *
                FROM Watching
                WHERE uID = %s
                AND mTitle = %s
                AND wDate > %s
                """, [request.POST.get("id"), request.POST.get("title"), request.POST.get("date")])
                record_later_than_input = cursor.fetchone()

                if record_later_than_input:
                    error_message = "Error! A later record exists!"
                else:
                    # Check if the watching date is earlier than the movie's release date
                    cursor.execute("""
                    SELECT *
                    FROM Movies
                    WHERE title = %s
                    AND releaseDate > %s
                    """, [request.POST.get("title"), request.POST.get("date")])
                    is_earlier_than_release_date = cursor.fetchone()

                    if is_earlier_than_release_date:
                        error_message = "Error! The date entered is earlier than the release date of the movie!"
                    else:
                        # If no errors, insert the new watching record
                        cursor.execute("""
                        INSERT INTO Watching (uID, mTitle, wDate, rating)
                        VALUES(%s, %s, %s, %s); 
                        """, [request.POST.get("id"), request.POST.get('title'), request.POST.get('date'), request.POST.get('rating')])
                        success_message = "Success! The watching record has been added."

    context = {
        "error_message": error_message,
        "success_message": success_message,
        "all_movies": all_movies,
        "all_users": all_users,
    }

    return render(request, 'RecordWatching.html', context)



