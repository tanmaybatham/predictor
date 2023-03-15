import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import warnings


class Computation:
    def _init_(self):
        self.prodffinal_1 = pd.DataFrame()
        self.dffinal_2 = pd.DataFrame()
        self.corr_user = pd.DataFrame()
        self.corr_ = pd.DataFrame()
        self.tc = ""
        self.tp = ""

    def computation(self, tc, tp):
        df = pd.read_csv('data/SampleUsageData9March.csv', encoding='unicode_escape')
        my_df = pd.DataFrame(df,
                             columns=['Order Date Time', 'Product Name', 'Quantity', 'Customer Name',
                                      'Region'])
        my_df.fillna(0)

        Product_matrix_UII = my_df.pivot_table(index='Product Name', columns='Customer Name', values='Quantity',
                                               aggfunc='sum', fill_value=0, sort=True)
        Product_matrix_UII

        Product_matrix_UII2 = Product_matrix_UII
        # saving the dataframe
        Product_matrix_UII.to_csv('Products_Customer_Matrix_withSum.csv')

        def SumToPercentage():
            i = 0
            minValues = Product_matrix_UII.min()
            maxValues = Product_matrix_UII.max()
            for cust in Product_matrix_UII.columns:
                Minval = minValues[i]
                Maxval = maxValues[i]

                for prd in Product_matrix_UII.index:
                    currValue = Product_matrix_UII[cust][prd]
                    newValue = (currValue - Minval) / (Maxval - Minval) * 100
                    Product_matrix_UII2[cust][prd] = newValue
                i = i + 1

        SumToPercentage()
        Product_matrix_UII2

        dfnew = round(Product_matrix_UII2[tc].reset_index(), 2)
        print("my tc", tc)
        dfnew.set_axis(['Product Name', 'Actual Usage'], axis='columns', inplace=True)

        Customer_matrix_UII = Product_matrix_UII.copy()
        Customer_matrix_UII = Customer_matrix_UII.T

        dfnew_customers = round(Product_matrix_UII2.T[tp].reset_index(), 2)
        dfnew_customers.set_axis(['Customer Name', 'Actual Usage'], axis='columns', inplace=True)

        corr_ = Product_matrix_UII2.T.corr(method='pearson')
        self.corr_ = corr_

        Customer_matrix_UII2 = Customer_matrix_UII
        corr_2 = Customer_matrix_UII2.corr(method='pearson')

        def recommendation_phaseCustomer(product):
            dataset = Customer_matrix_UII2
            # Gets recommendations for a customer by using a weighted average of every other customer usage
            totals = {}  # empty dictionary
            simSums = {}  # empty dictionary sum of similarity
            sim = 0
            for other in dataset:
                # don't compare me to myself
                print(other)
                if other == product:
                    continue
                sim = corr_2[product][other]
                # ignore scores of zero or lower
                if sim <= 0:
                    continue
                for item in dataset[other].index:
                    totals.setdefault(item, 0)
                    totals[item] += dataset[other][item] * sim
                    # sum of similarities
                    simSums.setdefault(item, 0)  # setdefault is key value
                    simSums[item] += sim
                    # Create the normalized list

            possible_usage = [(total / simSums[item], item) for item, total in totals.items()]
            possible_usage.sort(reverse=True)
            # returns the recommended items
            recommendataions_list = [(recommend_item, usage) for usage, recommend_item in possible_usage]
            return recommendataions_list

        assumed_correlation = pd.read_csv('data/assumed correlation2.csv',
                                          encoding='unicode_escape', index_col=0)
        
        assumed_correlation = ((assumed_correlation - 50) / 50)


        corr_user = assumed_correlation
        self.corr_user = corr_user

        def recommendation_phase_CustomerISV(product):
            dataset = Customer_matrix_UII2
            # Gets recommendations for a customer by using a weighted average of every other customer usage
            totals = {}  # empty dictionary
            simSums = {}  # empty dictionary sum of similarity
            sim = 0
            for other in dataset:
                # don't compare me to myself
                if other == product:
                    continue
                sim = corr_user[product][other]
                # ignore scores of zero or lower
                if sim <= 0:
                    continue
                for item in dataset[other].index:
                    totals.setdefault(item, 0)
                    totals[item] += dataset[other][item] * sim
                    # sum of similarities
                    simSums.setdefault(item, 0)  # setdefault is key value
                    simSums[item] += sim
                    # Create the normalized list

            possible_usage = [(total / simSums[item], item) for item, total in totals.items()]
            possible_usage.sort(reverse=True)
            # returns the recommended items
            recommendataions_list = [(recommend_item, usage) for usage, recommend_item in possible_usage]
            return recommendataions_list

        dataset = Customer_matrix_UII2
        # Anesthesia Machine

        a = recommendation_phaseCustomer(tp)
        b = recommendation_phase_CustomerISV(tp)
        if a != -1:

            dfResult = pd.DataFrame(columns=['Customer Name', 'Predicted Usage'])
            dfResult_isv = pd.DataFrame(columns=['Customer Name', 'Predicted Usage'])
            print('For customer : ', tc)
            for webseries, weights in a:
                new_row = {'Customer Name': webseries, 'Predicted Usage': round(weights, 2)}

                dfResult = dfResult.append(new_row, ignore_index=True)
            for webseries_isv, weights_isv in b:
                new_row_isv = {'Customer Name': webseries_isv, 'Predicted Usage': round(weights_isv, 2)}

                dfResult_isv = dfResult_isv.append(new_row_isv, ignore_index=True)

        dfResult_isv.set_axis(['Customer Name', 'ISV Predicted Usage'], axis='columns', inplace=True)

        Customer_matrix_UII4 = Customer_matrix_UII2.copy()
        dataset = Customer_matrix_UII2

        for tp in Customer_matrix_UII2.columns:
            if tp in dataset.columns:

                a = recommendation_phaseCustomer(tp)
                if a != -1:

                    print('For product : ', tp)
                    for webseries, weights in a:

                        if dataset[tp][webseries] < 50:
                            Customer_matrix_UII4[tp][webseries] = round(weights, 2)

        df_allpred = Customer_matrix_UII4.copy()
        dffinal_1 = pd.merge(dfnew_customers, dfResult_isv, on='Customer Name')
        dffinal_2 = pd.merge(dffinal_1, dfResult, on='Customer Name')
        self.dffinal_2 = dffinal_2
        prodf = round(df_allpred.T[tc].reset_index(), 2)
        prodffinal_1 = pd.merge(dfnew, prodf, on='Product Name')
        self.prodffinal_1 = prodffinal_1
        prodffinal_1.set_axis(['Product Name', 'Actual Usage', 'Predicted Usage'], axis='columns', inplace=True)

    def values(prodffinal_1, dffinal_2, corr_user, corr_):
        return prodffinal_1, dffinal_2, corr_user, corr_

    def getcorr_heatmap_user(self):
        return self.corr_user

    def getproducts(self):
        return self.prodffinal_1

    def getcustomers(self):

        return self.dffinal_2

    def getcorr_heatmap(self):
        return self.corr_


