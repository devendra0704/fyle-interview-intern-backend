
SELECT COUNT(*) AS count
FROM assignments
WHERE grade = 'A' AND teacher_id = (
    SELECT teacher_id
    FROM assignments
    GROUP BY teacher_id
    ORDER BY COUNT(*) DESC
    LIMIT 1
);



