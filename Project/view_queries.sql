"Views for Query 1"
CREATE VIEW TOP20
AS
SELECT TOP 20 title, genre, (budget - TotalCost) AS TotalRevenue
FROM Movies JOIN (
    SELECT mTitle, SUM(salary) AS TotalCost
    FROM ActorsInMovies AIM
    GROUP BY mTitle
) AS A ON A.mTitle = Movies.title
ORDER BY TotalRevenue DESC;


"Views for Query 2"
CREATE VIEW ImprovingMovies
AS
SELECT DISTINCT Watching.mTitle
FROM Watching JOIN ActorsInMovies AIM ON Watching.mTitle = AIM.mTitle
WHERE Watching.mTitle NOT IN (
    SELECT w1.mTitle
    FROM Watching W1 JOIN Watching W2 ON W1.mTitle = W2.mTitle AND W1.uID = W2.uID
    WHERE W1.wDate < W2.wDate
      AND W1.rating >= W2.rating
);


"Views for Query 3"
CREATE VIEW MoreThanAverageInCountry
AS
SELECT Users.uID, B.country
FROM Users JOIN (
    SELECT Users.uid, COUNT(Users.uID) AS WatchingsPerUser
    FROM Users JOIN Watching ON Users.uID = Watching.uID
    GROUP BY Users.uID
) AS A ON A.uID = Users.uID
           JOIN (
    SELECT country, (COUNT(mTitle) / COUNT(DISTINCT Users.uID)) AS AveragePerCountry
    FROM Users JOIN Watching ON Users.uID = Watching.uID
    GROUP BY country
) AS B ON B.country = Users.country
WHERE WatchingsPerUser > AveragePerCountry;


CREATE VIEW FakeFans
AS
SELECT A.uID, A.country, WatchingsPerUser
FROM MoreThanAverageInCountry MTAIC JOIN (
    SELECT *
    FROM Users
    WHERE uid NOT IN (
        SELECT Users.uID
        FROM Users JOIN Watching ON Users.uID = Watching.uID
                   JOIN (
            SELECT *
            FROM ActorsInMovies
        ) AS AIM ON AIM.mTitle = Watching.mTitle
        WHERE favActor = aName
    )
) AS A ON A.uID = MTAIC.uID
                                    JOIN (
    SELECT Users.uid, COUNT(Users.uID) AS WatchingsPerUser
    FROM Users JOIN Watching ON Users.uID = Watching.uID
    GROUP BY Users.uID
) AS C ON C.uID = MTAIC.uID;


CREATE VIEW MoreThan5FakeFans
AS
SELECT A.country, COUNT(A.uID) AS NumberOfFakeFans
FROM MoreThanAverageInCountry MTAIC JOIN (
    SELECT *
    FROM Users
    WHERE uid NOT IN (
        SELECT Users.uID
        FROM Users JOIN Watching ON Users.uID = Watching.uID
                   JOIN (
            SELECT *
            FROM ActorsInMovies
        ) AS AIM ON AIM.mTitle = Watching.mTitle
        WHERE favActor = aName
    )
) AS A ON A.uID = MTAIC.uID
GROUP BY A.country HAVING COUNT(A.uID) >= 5;

