create view public.delivery_report as
select
  di.school_sr as di_school_sr,
  di.school_name as di_school_name,

  di.eps as di_eps,
  di.eups as di_eups,
  di.ezphs as di_ezphs,
  di.e_total_attendance as di_e_total_attendance,

  di.ps as di_ps,
  di.ups as di_ups,
  di.zphs as di_zphs,
  di.total_attendance as di_total_attendance,

  di.rice_100 as di_rice_100,
  di.rice_75 as di_rice_75,
  di.rice_50 as di_rice_50,
  di.rice_25 as di_rice_25,
  di.rice_13 as di_rice_13,
  di.rice_vessels as di_rice_vessels,

  di.dal_150 as di_dal_150,
  di.dal_100 as di_dal_100,
  di.dal_75 as di_dal_75,
  di.dal_50 as di_dal_50,
  di.dal_25 as di_dal_25,
  di.dal_13 as di_dal_13,
  di.dal_vessels as di_dal_vessels,

  di.curry_100 as di_curry_100,
  di.curry_75 as di_curry_75,
  di.curry_50 as di_curry_50,
  di.curry_25 as di_curry_25,
  di.curry_13 as di_curry_13,
  di.curry_vessels as di_curry_vessels,

  di.curd_kg as di_curd_kg,
  di.snack_kg as di_snack_kg,
  ''::text AS "Time",
  ''::text AS "Singnature",
 
  di.route_name as Route,

from
  daily_indent di
  join menu m on di.dod_menu_id = m.id
where
  di.indent_date = (now() AT TIME ZONE 'Asia/Kolkata'::text)::date;
order by
ORDER BY di.route_name, di.school_sr  