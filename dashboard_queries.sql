--average of all reviews per item
select avg (rating) from review where item=%s;

--flag when menu item review is +-1 stdev from avg
select * from review
where date(review.time_stamp)=date(now()) and rating not between (select avg(rating)-stddev(rating) from review) and (select avg(rating)+stddev(rating) from review);

--average status availability in .5 hour increments per week
select avg(status) from statuses
where yearweek(statuses.time_stamp) = yearweek(curdate())
group by round (statuses.time_stamp / (30 * 60));

--current status availability aggregated within .5 hour
select avg(status) from statuses
where hour(statuses.time_stamp) = hour(curtime()) and date(statuses.time_stamp) = date(curdate()) and round(statuses.time_stamp / (30 * 60)) = round(now() / (30 * 60));
