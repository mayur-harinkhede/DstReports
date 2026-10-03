create view public.cummulative_report as
select
v.departure_order || ') ' || v.route_name as v_combined,


  sum(di.total_school) as di_total_school,
  sum(di.running_school) as di_running_school,

  sum(di.eps) as di_eps,
  sum(di.eups) as di_eups,
  sum(di.ezphs) as di_ezphs,
  sum(di.e_total_attendance) as di_e_total_attendance,

  sum(di.ps) as di_ps,
  sum(di.ups) as di_ups,
  sum(di.zphs) as di_zphs,
  sum(di.total_attendance) as di_total_attendance,

  sum(di.rice_100) as rice100,
  sum(di.rice_75) as rice75,
  sum(di.rice_50) as rice50,
  sum(di.rice_25) as rice25,
  sum(di.rice_13) as rice13,
  sum(di.rice_vessels) as di_rice_vessels,

  sum(di.dal_150) as dal150,
  sum(di.dal_100) as dal100,
  sum(di.dal_75) as dal75,
  sum(di.dal_50) as dal50,
  sum(di.dal_25) as dal25,
  sum(di.dal_13) as dal13,
  sum(di.dal_vessels) as di_dal_vessels,

  sum(di.curry_100) as curry100,
  sum(di.curry_75) as curry75,
  sum(di.curry_50) as curry50,
  sum(di.curry_25) as curry25,
  sum(di.curry_13) as curry13,
  sum(di.curry_vessels) as di_curry_vessels,


  sum(di.total_vessels) as di_total_vessels,

   sum(di.curd_kg) as di_curd_kg,
  sum(di.snack_kg) as di_snack_kg

from
  daily_indent di
  join menu m on di.dod_menu_id = m.id
  join vessels v on di.today_vessels_id = v.id
where
  di.indent_date = (now() AT TIME ZONE 'Asia/Kolkata'::text)::date
group by
  v.departure_order,
  v.route_name
order by
  v.departure_order;