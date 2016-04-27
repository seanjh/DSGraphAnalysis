# Select subreddit group names
select 
subreddit,subreddit_id,count(distinct(author))
from [fh-bigquery:reddit_comments.2015_05]
WHERE subreddit_id IN ('t5_2rmfx','t5_2ul7u','t5_2u3ta','t5_2r05i','t5_2qka0','t5_2yuej','t5_2qioo','t5_2qhqb','t5_2qh53','t5_2stl8')
group by subreddit,subreddit_id

select 
author
from [fh-bigquery:reddit_comments.2015_05]
     WHERE subreddit_id IN ('t5_2rmfx','t5_2ul7u','t5_2u3ta','t5_2r05i','t5_2qka0','t5_2yuej','t5_2qioo','t5_2qhqb','t5_2qh53','t5_2stl8')
group by author
having count(distinct(subreddit))  > 2


select 
count(case when numb_subreddits >=3 then 1 end) as authors_3,
count(case when numb_subreddits >=4 then 1 end) as authors_4,
count(case when numb_subreddits >=5 then 1 end) as authors_5,
count(case when numb_subreddits >=6 then 1 end) as authors_6,
count(case when numb_subreddits >=7 then 1 end) as authors_7,
count(case when numb_subreddits >= 8 then 1 end) as authors_8,
count(case when numb_subreddits >= 9  then 1 end) as authors_9
from (select 
author, count(distinct(subreddit)) as numb_subreddits
from [fh-bigquery:reddit_comments.2015_05]
      WHERE subreddit_id IN ('t5_2rmfx','t5_2ul7u','t5_2u3ta','t5_2r05i','t5_2qka0','t5_2yuej','t5_2qioo','t5_2qhqb','t5_2qh53','t5_2stl8')
group by author
having numb_subreddits > 2
order by 2)




select 
author1,author2,count(distinct subreddit) as intersection

from (
    SELECT a.author as author1, b.author as author2, a.subreddit as subreddit
    FROM FLATTEN((
      SELECT UNIQUE(author) author, subreddit
      FROM [fh-bigquery:reddit_comments.2015_05]
      WHERE subreddit_id IN ('t5_2rmfx','t5_2ul7u','t5_2u3ta','t5_2r05i','t5_2qka0','t5_2yuej','t5_2qioo','t5_2qhqb','t5_2qh53','t5_2stl8')
        and author in (select author
                      from [fh-bigquery:reddit_comments.2015_05]
                      WHERE subreddit_id IN ('t5_2rmfx','t5_2ul7u','t5_2u3ta','t5_2r05i','t5_2qka0','t5_2yuej','t5_2qioo','t5_2qhqb','t5_2qh53','t5_2stl8')
                      group by author
                      having count(distinct(subreddit))  > 3
                      )
      GROUP BY subreddit
    ),author) a
    left join 
    (FLATTEN((
      SELECT UNIQUE(author) author, subreddit
      FROM [fh-bigquery:reddit_comments.2015_05]
      WHERE subreddit_id IN ('t5_2rmfx','t5_2ul7u','t5_2u3ta','t5_2r05i','t5_2qka0','t5_2yuej','t5_2qioo','t5_2qhqb','t5_2qh53','t5_2stl8') 
        and author in (select author
                      from [fh-bigquery:reddit_comments.2015_05]
                           WHERE subreddit_id IN ('t5_2rmfx','t5_2ul7u','t5_2u3ta','t5_2r05i','t5_2qka0','t5_2yuej','t5_2qioo','t5_2qhqb','t5_2qh53','t5_2stl8')
                      group by author
                      having count(distinct(subreddit))  > 3
                      )
      GROUP BY subreddit
    ),author)) b on a.subreddit == b.subreddit
    limit 10000000
)
where author1 < author2
group by 1,2
having count(distinct subreddit) > 1
limit 1000000


SELECT author, count(unique(subreddit)) as numb_subreddits
FROM [fh-bigquery:reddit_comments.2015_05]
WHERE subreddit_id IN ('t5_2rmfx','t5_2ul7u','t5_2u3ta','t5_2r05i','t5_2qka0','t5_2yuej','t5_2qioo','t5_2qhqb','t5_2qh53','t5_2stl8') 
  and author in (select author
                from [fh-bigquery:reddit_comments.2015_05]
                     WHERE subreddit_id IN ('t5_2rmfx','t5_2ul7u','t5_2u3ta','t5_2r05i','t5_2qka0','t5_2yuej','t5_2qioo','t5_2qhqb','t5_2qh53','t5_2stl8')
                group by author
                having count(distinct(subreddit))  > 3
                )
group by author

