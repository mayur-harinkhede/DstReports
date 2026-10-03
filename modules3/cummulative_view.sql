create view public.cummulative_report as
select

  sum(di.rice_100) as R100,
  sum(di.rice_75) as R75,
  sum(di.rice_50) as R50,
  sum(di.rice_25) as R25,
  sum(di.rice_13) as R13,
  sum(di.rice_vessels) as Rice,

  sum(di.dal_150) as D150,
  sum(di.dal_100) as D100,
  sum(di.dal_75) as D75,
  sum(di.dal_50) as D50,
  sum(di.dal_25) as D25,
  sum(di.dal_13) as D13,
  sum(di.dal_vessels) as Dal,

  sum(di.curry_100) as C100,
  sum(di.curry_75) as C75,
  sum(di.curry_50) as C50,
  sum(di.curry_25) as C25,
  sum(di.curry_13) as C13,
  sum(di.curry_vessels) as Curry,
  ''::text AS "Time"

from
  daily_indent di
where
  di.indent_date = (now() AT TIME ZONE 'Asia/Kolkata'::text)::date
group by
  v.departure_order,
  v.route_name
order by
  v.departure_order;