SELECT
  Actor1Code, Actor1Name, Actor1Type1Code, Actor1CountryCode,
  Actor2Code, Actor2Name, Actor2Type1Code, Actor2CountryCode,
  MIN(Year) YearMin,
  MAX(Year) YearMax,
  EventCode,
  SUM(AvgTone) / SUM(NumArticles) AS consolidatedAvgTone,
  COUNT(1) AS eventCount
FROM [gdelt-bq:full.events]
WHERE
  (REGEXP_MATCH(EventCode, '^05.*') OR REGEXP_MATCH(EventCode, '^11.*')) AND
  Actor1Type1Code = 'GOV' AND
  (Actor2Type1Code = 'BUS' OR Actor2Type2Code = 'BUS') AND
  Actor1Name IS NOT NULL AND Actor2Name IS NOT NULL AND
  Actor1CountryCode IS NOT NULL AND
  Actor2CountryCode IS NOT NULL AND
  Actor1Code != Actor2Code
GROUP BY
  Actor1Code, Actor1Name, Actor1Type1Code, Actor2Code, Actor2Name,
  Actor2Type1Code, Actor2Type2Code, EventCode, Actor1CountryCode, Actor2CountryCode