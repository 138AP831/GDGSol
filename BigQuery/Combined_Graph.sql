SELECT 
  date, 
  'CO' AS gas, 
  CO_value AS ppm 
FROM `my-project-1635830540269.1.CO`

UNION ALL

SELECT 
  date, 
  'NO2' AS gas, 
  NO2_value AS ppm 
FROM `my-project-1635830540269.1.NO2`

UNION ALL

SELECT 
  date, 
  'Methane' AS gas, 
  methane_value AS ppm 
FROM `my-project-1635830540269.1.methane`

ORDER BY date;
