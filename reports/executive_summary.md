# Executive Summary

## Business Objective

This project analyzes online retail transaction data to understand sales
performance, product performance, market concentration, customer behavior,
and customer value.

## Data Preparation

The original transaction data was audited and cleaned before analysis.
Cancelled transactions, returns, invalid prices, missing identifiers, and
exact duplicates were handled according to documented rules.

Completed sales were separated from cancellations and returns. Customer-level
analysis only included transactions with known customer IDs.

## Overall Performance

- Gross completed-sales revenue: **10,642,110**
- Completed orders: **19,960**
- Known customers: **4,338**
- Average order value: **533.17**
- Cancellation rate: **15.69%**

## Main Sales Findings
1. **Overall Performance:**
The business shows strong performance! The dataset records a total revenue of £10,642,110.80 
generated from 19,962 completed orders, resulting in a solid Average Order Value (AOV) of 
£543.11.

2. **Monthly Performance:**
November 2011 stands out as the peak month for sales. However, the data for the very first and 
last months appears to be incomplete. These periods should be excluded before comparing monthly 
trends to avoid skewed results.

3. **Market Concentration:**
The United Kingdom drives the vast majority of the sales. This indicates a high dependence on a 
single market, exposing the business to potential regional risks.

4. **Product Performance:**
Interestingly, the top revenue generator isn't a physical item, but DOTCOM POSTAGE (shipping fees). 
This finding also highlights that products with the highest sales volume do not always bring in the 
most money for the company.

5. **Customer Concentration:**
The Top 10 VIP customers account for 10.82% of the known customer revenue. This reflects a moderate 
dependence on a small buyer group, suggesting that the company should maintain a targeted retention 
strategy to keep these key clients engaged.

6. **Cancellations:**
The overall cancellation rate is notably low at just 1.73%. As a next analytical step, it would be 
highly beneficial to drill down and see if these canceled invoices are tied to specific products or 
countries to identify any root causes.

## Customer Segmentation Findings

1. **High-value customers:** The highest-revenue segment was **Champions**,
   contributing **53.02%** of known-customer revenue.

2. **Customer concentration:** Champions represented only **14.96%** of known
   customers but generated **53.02%** of known-customer revenue.

3. **Retention risk:** At-risk customers represented **11.27%** of customers and
   **11.78%** of revenue. Because these customers purchased frequently or spent
   heavily in the past, they should receive targeted reactivation campaigns.

4. **Customer development:** Potential loyalists represented **10.28%** of
   customers. Second-purchase incentives and personalized recommendations
   could help move them into loyal segments.

5. **New customers:** New customers represented **2.19%** of the customer base.
   An onboarding and follow-up process could improve repeat purchasing.

## Recommendations

1. Retain champions and loyal customers using personalized loyalty benefits.
2. Prioritize high-value at-risk customers for reactivation campaigns.
3. Encourage potential loyalists to make additional purchases through
   targeted recommendations and second-purchase incentives.
4. Build an onboarding process for new customers.
5. Reduce dependence on highly concentrated products, markets, or customers
   where appropriate.

## Limitations

- The data represents one historical retailer.
- Customer demographic and marketing data are not available.
- Product costs and profit margins are unavailable, so the analysis measures
  revenue rather than profit.
- RFM segmentation is rule-based and does not predict future behavior.
- Customers without IDs cannot be included in customer segmentation.