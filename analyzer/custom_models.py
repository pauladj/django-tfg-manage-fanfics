import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from common.models import Fanfic, FandomFanfic, CharacterFanfic, Related


class Recommender:

    def __init__(self):
        self.dataframe = None
        self.indices = None
        self.cosine_sim = None

    def get_data(self):
        """ Get the appropiate data """
        fanfics_dataframe = Dataframer.get_fanfics_dataframe()

        fandoms_dataframe = Dataframer.get_fandoms_dataframe()

        fanfics_fandoms_dataframe = Dataframer.join_two_dataframes(
            fanfics_dataframe, "id", fandoms_dataframe, "fanfic__id", "inner")

        characters_dataframe = Dataframer.get_characters_dataframe()

        fanfics_fandoms_characters_dataframe = Dataframer.join_two_dataframes(
            fanfics_fandoms_dataframe, "id", characters_dataframe,
            "fanfic__id", "left")

        dataframe = Dataframer.join_column(
            fanfics_fandoms_characters_dataframe,
            ['data',
             'character__name_surname',
             'fandom__name'],
            'id')

        return dataframe

    def preprocess_data(self):
        """ Preprocess the data """
        count = CountVectorizer()
        count_matrix = count.fit_transform(self.dataframe['data'])
        self.cosine_sim = cosine_similarity(count_matrix, count_matrix)

    def get_recommendations(self, fanfic_id):
        # the index of the fanfic that matches the fanfic_id
        idx = self.indices[fanfic_id]

        # Get the pairwise similarity scores of all fanfics with that fanfic
        sim_scores = list(enumerate(self.cosine_sim[idx]))

        # Sort the fanfics based on the similarity scores
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # 4 most similar fanfics
        sim_scores = sim_scores[1:5]

        # Get the indices of the similar fanfics
        fanfics_indices = [i[0] for i in sim_scores]

        # Return their indices
        return self.dataframe['id'].iloc[fanfics_indices].to_list()

    def save_recommendations(self):
        """ Save recommendations"""
        # Delete previous recommendations
        Related.objects.all().delete()
        # Get current fanfics
        fanfics_ids = self.dataframe['id']
        for fanfic_id in fanfics_ids:
            fanfic_obj_one = Fanfic.objects.filter(id=fanfic_id)
            if fanfic_obj_one.exists():
                fanfic_obj_one = fanfic_obj_one.first()
                recommended_fanfics_ids = self.get_recommendations(fanfic_id)
                for fanfic_id_two in recommended_fanfics_ids:
                    fanfic_obj_two = Fanfic.objects.filter(id=fanfic_id_two)
                    if fanfic_obj_two.exists():
                        fanfic_obj_two = fanfic_obj_two.first()
                        Related.objects.create(fanfic_one=fanfic_obj_one,
                                               fanfic_two=fanfic_obj_two)

    def start(self):
        """ Start the recommendation system and evaluate the data"""
        # First get the data in a dataframe
        self.dataframe = self.get_data()
        # Index it
        self.indices = Dataframer.create_map(self.dataframe, 'id')
        # Preprocess it
        self.preprocess_data()
        # Save the recommendations for each fanfic
        self.save_recommendations()


class Dataframer:

    @staticmethod
    def get_fanfics_dataframe():
        """ Get the fanfic dataframe from the database """
        fanfics_data = Fanfic.objects.values('id', 'language', 'genre1',
                                             'genre2',
                                             'genre3',
                                             'genre4', 'author')
        fanfics_dataframe = Dataframer.query_to_dataframe(
            fanfics_data)
        fanfics_dataframe = Dataframer.join_column(fanfics_dataframe,
                                                   ['author', 'genre1',
                                                    'genre2', 'genre3',
                                                    'genre4', 'language'],
                                                   'id')
        return fanfics_dataframe

    @staticmethod
    def get_fandoms_dataframe():
        """ Get the fandoms dataframe from the database """
        fandoms_data = FandomFanfic.objects.select_related(
            'fanfic, fandom').values(
            'fanfic__id',
            'fandom__name')
        fandoms_dataframe = Dataframer.query_to_dataframe(
            fandoms_data)
        fandoms_dataframe.sort_values(by='fanfic__id', inplace=True)
        fandoms_dataframe = Dataframer.remove_duplicated_rows_content(
            fandoms_dataframe,
            "fandom__name",
            "fanfic__id")
        return fandoms_dataframe

    @staticmethod
    def get_characters_dataframe():
        """ Get the characters dataframe from the database """
        characters_data = CharacterFanfic.objects.select_related(
            'character, fanfic').values(
            'character__name_surname',
            'fanfic__id')
        characters_dataframe = Dataframer.query_to_dataframe(
            characters_data)
        characters_dataframe.sort_values(by='fanfic__id', inplace=True)
        characters_dataframe = Dataframer.remove_duplicated_rows_content(
            characters_dataframe,
            "character__name_surname",
            "fanfic__id")
        return characters_dataframe

    @staticmethod
    def query_to_dataframe(query_set):
        """ Convert result queryset to dataframe """
        dataframe = pd.DataFrame.from_records(query_set)
        format = lambda x: str(x).lower().replace(' ', '') + " " if x is not \
                                                                    None \
                                                                    and x != "" else ""
        return dataframe.applymap(format)

    @staticmethod
    def join_column(dataframe, columns_names, column_to_keep):
        """ Join columns """
        final_dataframe = None
        for name in columns_names:
            if final_dataframe is None:
                final_dataframe = dataframe[name]
            else:
                final_dataframe += dataframe[name]

        final_dataframe = final_dataframe.to_frame('data').join(
            dataframe[column_to_keep])
        return final_dataframe

    @staticmethod
    def remove_duplicated_rows_content(df, data_column_name, id_column):
        duplicated_rows = df[df.duplicated([id_column], keep=False)]

        rows_to_change = []
        rows_to_delete = []
        new_values = []

        fanfic_index = None

        for index, row in duplicated_rows.iterrows():
            index_now = row[id_column]
            if fanfic_index is None or index_now != fanfic_index:
                fanfic_index = index_now
                rows_to_change.append(index)
                new_values.append(row[data_column_name])
            elif index_now == fanfic_index:
                rows_to_delete.append(index)
                old_value = new_values[len(new_values) - 1]
                new_values[len(new_values) - 1] = old_value + " " + row[
                    data_column_name]

        for r in rows_to_delete:
            df = df.drop(r)

        for idx, r in enumerate(rows_to_change):
            df.loc[r, data_column_name] = new_values[idx]
        return df

    @staticmethod
    def join_two_dataframes(one_df, one_key, two_df, two_key, union_type):
        final_df = pd.merge(one_df, two_df, left_on=[one_key], right_on=[
            two_key], how=union_type)
        if one_key != two_key:
            final_df = final_df.drop(two_key, axis=1)
        final_df = final_df.fillna('')
        return final_df

    @staticmethod
    def create_map(dataframe, column_to_index):
        """ Create a reverse map of indices and fanfic indexes """
        indices = pd.Series(dataframe.index, index=dataframe[
            column_to_index]).drop_duplicates()
        return indices
