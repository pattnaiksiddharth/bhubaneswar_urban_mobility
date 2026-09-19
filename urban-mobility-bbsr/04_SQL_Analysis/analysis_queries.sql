-- ============================================================
--  Bhubaneswar Urban Mobility – SQL Analysis Queries
--  Database: 04_SQL_Analysis/bhubaneswar_mobility.db
-- ============================================================


-- ────────────────────────────────────────────────────────────
-- Q1: Which bus stops attract the highest daily ridership,
--     and what type of land-use dominates each stop?
-- ────────────────────────────────────────────────────────────
SELECT
    stop_id,
    dominant_type,
    total_daily_demand,
    demand_quartile,
    primary_flag
FROM dim_stops
ORDER BY total_daily_demand DESC
LIMIT 10;


-- ────────────────────────────────────────────────────────────
-- Q2: How many routes fall under each planning recommendation
--     category (primary_flag)?  Helps size the intervention
--     budget by category.
-- ────────────────────────────────────────────────────────────
SELECT
    primary_flag,
    COUNT(*) AS route_count
FROM dim_routes
GROUP BY primary_flag
ORDER BY route_count DESC;


-- ────────────────────────────────────────────────────────────
-- Q3: Which routes are MOST URGENT – flagged for increased
--     frequency AND located near a congestion point?  Shows
--     the net daily benefit and demand so planners can
--     prioritise investment.
-- ────────────────────────────────────────────────────────────
SELECT
    dr.route_id,
    dr.stop_id,
    dr.primary_flag,
    dr.near_congestion_point,
    ds.total_daily_demand,
    cba.net_daily_benefit
FROM dim_routes AS dr
JOIN dim_stops         AS ds  ON dr.stop_id  = ds.stop_id
JOIN cost_benefit_analysis AS cba ON dr.route_id = cba.route_id
WHERE dr.primary_flag       = 'Increase Frequency'
  AND dr.near_congestion_point = 1          -- SQLite stores TRUE as 1
ORDER BY ds.total_daily_demand DESC;


-- ────────────────────────────────────────────────────────────
-- Q4: What is the average net daily benefit for each planning
--     recommendation category?  Reveals which flag category
--     is most financially viable on average.
-- ────────────────────────────────────────────────────────────
SELECT
    dr.primary_flag,
    ROUND(AVG(cba.net_daily_benefit), 2) AS avg_net_daily_benefit,
    COUNT(*)                              AS route_count
FROM dim_routes            AS dr
JOIN cost_benefit_analysis AS cba ON dr.route_id = cba.route_id
GROUP BY dr.primary_flag
ORDER BY avg_net_daily_benefit DESC;


-- ────────────────────────────────────────────────────────────
-- Q5: What is the total cost, total revenue, and net benefit
--     across ALL flagged routes combined?  Single summary row
--     for executive reporting.
-- ────────────────────────────────────────────────────────────
SELECT
    COUNT(*)                                        AS total_routes,
    ROUND(SUM(additional_daily_cost),     2)        AS total_daily_cost,
    ROUND(SUM(additional_daily_revenue),  2)        AS total_daily_revenue,
    ROUND(SUM(net_daily_benefit),         2)        AS total_net_daily_benefit,
    ROUND(AVG(roi_ratio),                 4)        AS avg_roi_ratio
FROM cost_benefit_analysis;


-- ────────────────────────────────────────────────────────────
-- Q6: Which land-use type generates the most total demand?
--     Ranked descending to highlight the dominant demand
--     drivers across the network.
-- ────────────────────────────────────────────────────────────
SELECT
    dominant_type,
    ROUND(SUM(total_daily_demand), 2) AS total_demand,
    COUNT(*)                           AS stop_count,
    ROUND(AVG(total_daily_demand), 2) AS avg_demand_per_stop
FROM dim_stops
GROUP BY dominant_type
ORDER BY total_demand DESC;


-- ────────────────────────────────────────────────────────────
-- Q7: How accurate were the Prophet forecasts over the last
--     15 days of the forecast period?  Shows actual vs
--     forecast and absolute daily error for model validation.
-- ────────────────────────────────────────────────────────────
SELECT
    date,
    ROUND(actual_demand,      2) AS actual_demand,
    ROUND(prophet_forecast,   2) AS prophet_forecast,
    ROUND(ABS(actual_demand - prophet_forecast), 2) AS absolute_error
FROM fact_daily_forecast
WHERE prophet_forecast IS NOT NULL
ORDER BY date DESC
LIMIT 15;


-- ────────────────────────────────────────────────────────────
-- Q8: Which 5 routes deliver the best return on investment,
--     considering only routes with a positive net daily
--     benefit?  Guides prioritisation of limited capital.
-- ────────────────────────────────────────────────────────────
SELECT
    cba.route_id,
    dr.stop_id,
    dr.primary_flag,
    ROUND(cba.roi_ratio,         4) AS roi_ratio,
    ROUND(cba.net_daily_benefit, 2) AS net_daily_benefit,
    ROUND(cba.additional_daily_cost, 2) AS daily_cost
FROM cost_benefit_analysis AS cba
JOIN dim_routes             AS dr ON cba.route_id = dr.route_id
WHERE cba.net_daily_benefit > 0
ORDER BY cba.roi_ratio DESC
LIMIT 5;
