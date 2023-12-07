import pandas as pd
from pyhpo import HPOSet
from Custom_Scoring import *
import numpy as np


class HpoCompare:
    def __init__(self, ontology, background_data_url, method='custom_jaccardIC', kind='omim', combine='funSimAvg'):
        self.ontology = ontology
        self.background_data = background_data_url
        self.method = method
        self.kind = kind
        self.combine = combine
        self.fileRows = self.__openFile(self.background_data)
        self.patient_dict = self.__createPatientDict(self.fileRows)

    def calculateSimilarity(self, input_terms):
        ''''Calculate similarity scores between input patient and every patient in background data.
        Required: input_terms = list of HPO terms for input patient '''
        patient_list = list(self.patient_dict.keys())
        scores_list=[]
        ##create HPOSet object for input patient
        try:
            input_HPOSet = HPOSet.from_queries(input_terms)
        except RuntimeError:
            for term in input_terms:
                try:
                    term_ont = self.ontology.get_hpo_object(term)
                except RuntimeError:
                    print(term, 'is not a valid HPO term')
                    break
        ##compare input patient to list of background patients
        for patient in patient_list:
            try:
                patient_HPOSet = HPOSet.from_queries(self.patient_dict[patient])
            except RuntimeError:
                for term in self.patient_dict[patient]:
                    try:
                        ont=self.ontology.get_hpo_object(term)
                    except RuntimeError:
                        print(term, 'is not a valid HPO term')
                        break
            simScore = input_HPOSet.similarity(patient_HPOSet, method=self.method, kind=self.kind, combine=self.combine)
            scores_list.append([patient, simScore])

        scores_dict = self.__rankedDict(scores_list) #create dictionary of scores and ranks
        return scores_dict

    #Utility Internal Methods ----------------------------------------------------------------------------------------------

    def __openFile(self, infilename):
        rows = pd.read_csv(infilename)
        return rows

    def __createPatientDict(self, new_rows):
        ID_list = list(new_rows['ID'])
        patient_dict = {}
        for id in ID_list:
            terms = list(new_rows.loc[new_rows['ID'] == id]['Terms'])
            #terms = list(new_rows[new_rows['ID'].str.contains(id)]['Terms'])
            termsList = terms[0].split('; ')
            patient_dict[id] = termsList
        return patient_dict

    def __rankedDict(self, scores_list):
        """
        Create dictionary where keys=background patients; 
        score_dict[patient]['Score']=simScore to query
        score_dict[patient]['Rank'] = rank to query (between 1 and # patients)
        """
        # Sort the scores list in descending order based on scores
        sorted_scores = sorted(scores_list, key=lambda x: x[1], reverse=True)

        # Create a dictionary and assign rank while iterating
        score_dict = {}
        for rank, (patient, score) in enumerate(sorted_scores, start=1):
            score_dict[patient] = {'Score': score, 'Rank': rank}
        return score_dict
