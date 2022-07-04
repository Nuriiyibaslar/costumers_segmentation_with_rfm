# Customer Segmentation with RFM

#1 - Business Problem
#2 - Business Understanding
# 3 - Data Preparation
# 4 - Calculation of RMF Metrics
# 5 - Calculating RMF Scores
# 6 - Creating/Analysing RMF Segments
#7 - Functionalizing the entire process

##############
#1. Business Problem
###############

# An e-commerce company wants to segment its customers and determine marketing strategies according to these segments.

# Dataset Story
# https://archive.ics.uci.edu/ml/datasets/Online+Retail+II

# The data set named Online Retail II was created by a UK-based online store.
# Includes sales from 01/12/2009 to 09/12/2011.

# Variables

# InvoiceNo: Invoice number. The unique number of each transaction, that is, the invoice. Aborted operation if it starts with C.
# StockCode: Product code. Unique number for each product.
# Description: Product name
# Quantity: Number of products. It expresses how many of the products on the invoices have been sold.
# InvoiceDate: Invoice date and time.
# UnitPrice: Product price (in GBP)
# CustomerID: Unique customer number
# Country: Country name. Country where the customer lives.

###############
# 2. Data Understanding
###############

import datetime as dt
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.3f' % x) # show how many digits after the comma of numeric variables

df_ = pd.read_excel("/Users/nuri/PycharmProjects/pythonProject/pythonProject_n/dsmlbc_nuri/notes_dsmlbc/week_2/crm_analytics/datasets/online_retail_II.xlsx",sheet_name="Year 2009-2010")
df_.head()
df = df_.copy()

# Let's look at the variables
# is the invoice ID of the invoice. It has to repeat more than once. This invoice can contain more than one product.
# Quantity shows how many units of that product were purchased.
# We need to multiply the Quantity by the Price to find out how much was paid for the product.

df.shape
df.isnull().sum() # how many missing values are there
# these missing values will be deleted
# because we are doing a customer-oriented segmentation
# and we cannot work with variables that do not have a customer-id


# what is the number of unique products?
df["Description"].nunique()

# how many of which product do you have?
df["Description"].value_counts()

# what is the most ordered product?

df.groupby("Description").agg({"Quantity" : "sum"}).head() # how many were ordered in total

# ! There is a problem here that Quantity is negative, but we'll just ignore it for now.
# we will get rid of this situation in data preprocessing.

df.groupby("Description").agg({"Quantity" : "sum"}).sort_values("Quantity",ascending=False).head()

df["Invoice"].nunique() # unique invoice number
df["Country"].nunique()
df["Country"].value_counts()


# total amount of money earned per invoice

df["TotalPrice"] = df["Price"] * df["Quantity"]
df.groupby("Invoice").agg({"TotalPrice": "sum"}).sum()

# We will need to deduplicate these tables on the way to segmentation

#######################
# 3 (Data Preparation)
#######################

df.isnull().sum()
df.dropna(inplace=True)

# We have another problem mentioned in the dataset story.
# In the invoice variable, there were expressions with C at the beginning. These represent returns.

df = df[~df["Invoice"].str.contains("C",na=False)]

###############################################################
# 4. Calculating RFM Metrics
###############################################################

# Recency, Frequency, Monetary

# We prepared the data set for calculating RMF metrics. We got to know the structure of the data set
# What we will do now is to calculate this recency frequency and monetary values for each customer.

# The mathematical equivalent of the recency is the date the analysis was made minus the date the relevant customer made the last purchase.
# Frequency is the total purchase made by the customer.
# What is Monetary? It is the total money left by the customer as a result of the total purchases made.

# First of all, we need to specify the day we perform the analysis.

# Since this data set is an old data set and we were not living at that time, we can accept 2 days after the last transaction date as the date of analysis.

df["InvoiceDate"].max()

today_date = dt.datetime(2010,12,11) # keep the entered date in time variable form
type(today_date)

# the unique invoice number of each customer gives us the frequency.
# Recency today_date - Max date of each customer
# sum of total prices is also monetary


rmf = df.groupby("Customer ID").agg({"InvoiceDate" : lambda InvoiceDate : (today_date - InvoiceDate.max()).days,
                               "Invoice" : lambda Invoice : Invoice.nunique(),
                               "TotalPrice" : lambda TotalPrice :  TotalPrice.sum() })


rmf.head()
rmf.columns = ["recency","frequency","monetary"]
rmf.describe().T

# we see zero monetary value at min value,
# this is not a situation we want and let's get rid of it

rmf = rmf[rmf["monetary"] > 0]

###################
# 5. Calculating RFM Scores)
###################


rmf["recency_score"] = pd.qcut(rmf["recency"], 5, labels=[5, 4, 3, 2, 1])

# qcut will be sorted from smallest to largest, divided into 5 parts, then labeled with the labels argument
rmf.head()

# rmf["frequency_score"] = pd.qcut(rmf["frequency"],5,labels=[1,2,3,4,5]) gives an error when we write it with this code,
# because the same frequency numbers fall into the ranges it is divided into.
# We get rid of the problem with rank(method="First"),
# what does it mean, assign the first class you see first.

rmf["frequency_score"] = pd.qcut(rmf["frequency"].rank(method="first"),5,labels=[1,2,3,4,5])
rmf["monetary_score"] = pd.qcut(rmf["monetary"],5,labels=[1,2,3,4,5])

# now we need to create score over these variables
# from non-monetary r and f values

rmf["RMF_SCORE"] = rmf["recency_score"].astype(str) + rmf["frequency_score"].astype(str)

# A situation assessment

rmf.describe().T

# who should we say are my champions?

rmf[rmf["RMF_SCORE"]=="55"]


##################
# 6. Creating & Analysing RFM Segments)
##################

# There are classifications accepted in the sector.
# Let's write the names of these segments in order to increase the readability of our numerical evaluations.

# regex
# RegEx can be used to check if a string contains the specified search pattern.

# RFM nomenclature

seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}

# Express this regex by writing a simple code ( Regular expression ) It provides pattern matching and capturing structure.

rmf["segment"] = rmf["RMF_SCORE"].replace(seg_map,regex=True)
rmf.head()

# We need to analyze these generated segments.
# Analysis of segments means trying to understand their structure in this way.

rmf[["segment","recency","frequency","monetary"]].groupby("segment").agg(["mean","count"])

# Let's say the sales and marketing department wants the need attention class from us. Let's say we want to focus on this.

rmf[rmf["segment"] == "need_attention"].head()
rmf[rmf["segment"] == "need_attention"].index # ids of customers in this class

new_df = pd.DataFrame()
new_df["new_customer_id"] = rmf[rmf["segment"] == "new_customers"].index

new_df["new_customer_id"] = new_df["new_customer_id"].astype(int) # Getting rid of decimals in ID

# export in excel or csv form

new_df.to_csv("new_customers_sending.csv")
rmf.to_csv("all_segments")

###############
# 7. Functionalizing the Whole Process
###############

# When we write a function, this function has some properties that must be carried by the basic programming principles. Like the do one thing principle
# Like don't repeat yourself, and another like being modular

# In fact, a separate function can be written for each layer in the entire RMF process.
# And so that the middleware can be controlled more easily, it may be desirable to intervene in a step of the function during the flow of changes in the data set.
# If it is written separately and written as return, those middle layers can be interfered more.
# But our understanding of evaluation here will be
# We are writing a script, in summary we represent it with a function. So when we call this function and ask this func for a specified dataframe
# We want the analysis process to be completed very quickly and a result to be printed.


def create_rfm(dataframe, csv=False):
    # PREPARING THE DATA
    dataframe["TotalPrice"] = dataframe["Quantity"] * dataframe["Price"]
    dataframe.dropna(inplace=True)
    dataframe = dataframe[~dataframe["Invoice"].str.contains("C", na=False)]

    # CALCULATION OF RFM metrics
    today_date = dt.datetime(2011, 12, 11)
    rfm = dataframe.groupby('Customer ID').agg({'InvoiceDate': lambda date: (today_date - date.max()).days,
                                                'Invoice': lambda num: num.nunique(),
                                                "TotalPrice": lambda price: price.sum()})
    rfm.columns = ['recency', 'frequency', "monetary"]
    rfm = rfm[(rfm['monetary'] > 0)]

    # CALCULATION OF RFM SCORES
    rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
    rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
    rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])

    # cltv_df scores converted to categorical value and added to df
    rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) +
                        rfm['frequency_score'].astype(str))


    # NAMING OF SEGMENTS
    seg_map = {
        r'[1-2][1-2]': 'hibernating',
        r'[1-2][3-4]': 'at_risk',
        r'[1-2]5': 'cant_loose',
        r'3[1-2]': 'about_to_sleep',
        r'33': 'need_attention',
        r'[3-4][4-5]': 'loyal_customers',
        r'41': 'promising',
        r'51': 'new_customers',
        r'[4-5][2-3]': 'potential_loyalists',
        r'5[4-5]': 'champions'
    }

    rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)
    rfm = rfm[["recency", "frequency", "monetary", "segment"]]
    rfm.index = rfm.index.astype(int)

    if csv:
        rfm.to_csv("rfm.csv")

    return rfm

df = df_.copy()

rmf_new = create_rfm(df)

# This analysis can be repeated periodically. We created these segments in a certain month of a certain year.
# The customers in these segments may change in the next month or in the following months.
# It is very critical to observe the changes here. We need to be able to run this business every month.
# We should be able to report the changes in the segments that occur after working every month,
# and for example, a report was created in the first month and we sent a list to a certain department to take action,
# that department took action, but what will happen next?
