SELECT COUNT(*) FROM customers;

--Query 1 — Portfolio Overview
SELECT COUNT(*) AS total_customers,
 SUM(Delinquent_Account) AS total_delinquent,
 ROUND(AVG(Delinquent_Account) * 100, 1) AS delinquency_rate_pct,
 ROUND(AVG(Missed_Payments), 2) AS avg_missed_payments
FROM customers;

-- Query 2 — Delinquency by Missed Payments
SELECT Missed_Payments, COUNT(*) AS total_customers,
 SUM(Delinquent_Account) AS delinquent_count,
 ROUND(AVG(Delinquent_Account) * 100, 1) AS delinquency_rate_pct
FROM customers
GROUP BY Missed_Payments
ORDER BY Missed_Payments ASC;



-- Query 3 — Risk Scoring with CTE
WITH risk_scored AS (
    SELECT
        Customer_ID,
        Employment_Status,
        Credit_Card_Type,
        Missed_Payments,
        Delinquent_Account,

        -- Give each customer a risk score out of 9
        (CASE WHEN Missed_Payments >= 5 THEN 3
              WHEN Missed_Payments >= 3 THEN 2
              WHEN Missed_Payments >= 1 THEN 1
              ELSE 0 END
        +
        CASE WHEN Credit_Utilization > 0.8 THEN 2
             WHEN Credit_Utilization > 0.6 THEN 1
             ELSE 0 END
        +
        CASE WHEN Employment_Status = 'Unemployed' THEN 2
             WHEN Employment_Status = 'Self-employed' THEN 1
             ELSE 0 END) AS risk_points

    FROM customers
)

SELECT
    CASE
        WHEN risk_points >= 5 THEN 'High Risk'
        WHEN risk_points >= 3 THEN 'Medium Risk'
        ELSE 'Low Risk'
    END AS risk_tier,
    COUNT(*) AS customer_count,
    ROUND(AVG(Delinquent_Account) * 100, 1) AS delinquency_rate_pct
FROM risk_scored
GROUP BY risk_tier
ORDER BY delinquency_rate_pct DESC;



-- Query 4 — Creating the View
CREATE VIEW IF NOT EXISTS customer_risk_view AS
SELECT
    Customer_ID,
    Age,
    [Age Bracket],
    Employment_Status,
    Credit_Card_Type,
    Location,
    Income,
    Credit_Score,
    ROUND(Credit_Utilization * 100, 1) AS credit_util_pct,
    Missed_Payments,
    Loan_Balance,
    ROUND(Debt_to_Income_Ratio * 100, 1) AS dti_pct,
    Delinquent_Account,

    -- Payment risk score (0-12)
    (CASE WHEN Month_1 = 'Missed' THEN 2 WHEN Month_1 = 'Late' THEN 1 ELSE 0 END +
     CASE WHEN Month_2 = 'Missed' THEN 2 WHEN Month_2 = 'Late' THEN 1 ELSE 0 END +
     CASE WHEN Month_3 = 'Missed' THEN 2 WHEN Month_3 = 'Late' THEN 1 ELSE 0 END +
     CASE WHEN Month_4 = 'Missed' THEN 2 WHEN Month_4 = 'Late' THEN 1 ELSE 0 END +
     CASE WHEN Month_5 = 'Missed' THEN 2 WHEN Month_5 = 'Late' THEN 1 ELSE 0 END +
     CASE WHEN Month_6 = 'Missed' THEN 2 WHEN Month_6 = 'Late' THEN 1 ELSE 0 END)
     AS payment_risk_score,

    -- Risk tier
    CASE
        WHEN (CASE WHEN Missed_Payments >= 5 THEN 3
                   WHEN Missed_Payments >= 3 THEN 2
                   WHEN Missed_Payments >= 1 THEN 1 ELSE 0 END
             + CASE WHEN Credit_Utilization > 0.8 THEN 2
                    WHEN Credit_Utilization > 0.6 THEN 1 ELSE 0 END
             + CASE WHEN Employment_Status = 'Unemployed' THEN 2
                    WHEN Employment_Status = 'Self-employed' THEN 1 ELSE 0 END) >= 5
        THEN 'High Risk'
        WHEN (CASE WHEN Missed_Payments >= 5 THEN 3
                   WHEN Missed_Payments >= 3 THEN 2
                   WHEN Missed_Payments >= 1 THEN 1 ELSE 0 END
             + CASE WHEN Credit_Utilization > 0.8 THEN 2
                    WHEN Credit_Utilization > 0.6 THEN 1 ELSE 0 END
             + CASE WHEN Employment_Status = 'Unemployed' THEN 2
                    WHEN Employment_Status = 'Self-employed' THEN 1 ELSE 0 END) >= 3
        THEN 'Medium Risk'
        ELSE 'Low Risk'
    END  AS risk_tier

FROM customers;




-- Verifying it works
SELECT risk_tier, COUNT(*) AS customers, ROUND(AVG(Delinquent_Account)*100,1) AS delinquency_rate_pct
FROM customer_risk_view
GROUP BY risk_tier
ORDER BY delinquency_rate_pct DESC;

SELECT ML_Risk_Tier,
       COUNT(*) AS customers,
       ROUND(AVG(Delinquent_Account) * 100, 1) AS actual_delinquency_pct
FROM scored_customers
GROUP BY ML_Risk_Tier
ORDER BY actual_delinquency_pct DESC;