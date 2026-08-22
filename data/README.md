\# razorshield-risk-quard — Synthetic Dataset



\## Purpose



This directory contains synthetic data used for developing and

evaluating the razorshield-risk-quard chargeback risk investigation system.



\## Important



No real customer, payment, merchant, or financial data is used.



All records are artificially generated for research, development,

testing, and demonstration purposes.



\## Datasets



\### customers.csv



Contains synthetic customer-level information.



Main fields:



\- customer\_id

\- account\_age\_days

\- previous\_transactions

\- successful\_transactions

\- previous\_chargebacks

\- previous\_refunds

\- known\_devices

\- average\_order\_value



\### transactions.csv



Contains synthetic transaction information.



Main fields:



\- transaction\_id

\- customer\_id

\- amount

\- payment\_method

\- device\_id

\- ip\_country

\- transaction\_time

\- authentication\_status

\- previous\_transactions



\### orders.csv



Contains synthetic order and delivery information.



Main fields:



\- order\_id

\- transaction\_id

\- product\_category

\- product\_value

\- shipping\_address

\- delivery\_status

\- delivery\_date

\- refund\_status



\### chargebacks.csv



Contains synthetic chargeback cases.



Main fields:



\- chargeback\_id

\- transaction\_id

\- reason\_code

\- claimed\_amount

\- claim\_date

\- customer\_reason

\- status



\### evidence.csv



Contains synthetic evidence associated with transactions.



Evidence types include:



\- payment authentication

\- delivery confirmation

\- refund record



\## Data Generation



The dataset is generated programmatically using:



\- Python

\- NumPy

\- Pandas



A fixed random seed is used to make dataset generation reproducible.



\## Intended ML Target



The chargeback records will later be used to construct the supervised

learning target for the risk prediction model.



The model will estimate:



`chargeback\_risk\_probability`



The exact target construction and feature engineering methodology

will be documented in the ML stage.



\## Disclaimer



This dataset is synthetic and does not represent actual merchant,

customer, transaction, or chargeback behavior.

