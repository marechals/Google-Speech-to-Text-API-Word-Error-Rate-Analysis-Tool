from model.configuration import Configuration
from model.nlp import NLPModel

class IOHandler(object):
    _result_path = ''
    _result_file_name = 'results.csv'
    _csv_header = 'AUDIO_FILE, MODEL, ENHANCED, LANGUAGE, ALTERNATIVE_LANGS, PHRASE_HINTS_APPLIED, BOOST, REF_WORD_COUNT, REF_ERROR_COUNT , WER,STEMMING_APPLIED , STOP_WORDS_REMOVED, NUMBER_TO_WORD_CONVERSION, CONTRACTIONS_EXPANDED, INSERTIONS, DELETIONS, SUBSTITUTIONS, DELETED_WORDS, INSERTED_WORDS, SUBSTITUTE_WORDS\n'
    _csv_header_written = False
    configuration = Configuration()
    nlp_model = NLPModel()
    _queue_file_name = 'queue.txt'

    def set_queue_file_name(self, name):
        self._queue_file_name = name

    def get_queue_file_name(self):
        return self._queue_file_name

    def set_result_path(self, result_path):
        self._result_path = result_path

    def get_result_path(self):
        return self._result_path

    def write_csv_header(self):
        import os
        if not self._csv_header_written:
            full_path = f'{self.get_result_path()}/{self._result_file_name}'
            # if path does not exists, make it
            if not os.path.exists(self.get_result_path()):
                os.makedirs(self.get_result_path())

            with open(full_path, 'w') as file:
                try:
                    file.write(self._csv_header)
                except IOError as i:
                    print(f'Can not write csv header: {i}')
                except FileNotFoundError as x:
                    print(f'Can not find csv file: {x}')
            self._csv_header_written = True

    def update_csv(self, uri, configuration, nlp_model, word_count_list =None ,ref_total_word_count = 0, ref_error_count = 0, word_error_rate =0, ins=0, deletions=0, subs=0 ):
        import logging
        logging.basicConfig(filename='wer_app.log')
        logger = logging.getLogger(__name__)
        from collections import OrderedDict
        deleted_words_dict = dict()
        inserted_words_dict = dict()
        substitute_words_dict = dict()

        if word_count_list:
            try:
                deleted_words_dict  = OrderedDict(sorted(word_count_list[0].items(), key=lambda x: x[1]))
                inserted_words_dict  = OrderedDict(sorted(word_count_list[1].items(), key=lambda x: x[1]))
                substitute_words_dict = OrderedDict(sorted(word_count_list[2].items(), key=lambda x: x[1]))
            except TypeError as t:
                string = f'{t}'
                logger.debug(string)
                print(string)
                deleted_words_dict = None
                inserted_words_dict = None
                substitute_words_dict = None
        deleted_words = ''
        inserted_words = ''
        substitute_words = ''
        if deleted_words_dict:
            for k, v in deleted_words_dict.items():
                deleted_words+= f'{k}:{v}, '
        if inserted_words_dict:
            for k, v in inserted_words_dict.items():
                inserted_words+=  f'{k}:{v}, '
        if substitute_words_dict:
            for k, v in substitute_words_dict.items():
                substitute_words+=  f'{k}:{v}, '

        full_path = f'{self.get_result_path()}/{self._result_file_name}'
        alts = ''
        for item in (configuration.get_alternative_language_codes()):
            alts+=item + ' '
        string = f'{uri}, {configuration.get_model()}, {configuration.get_use_enhanced()}, {configuration.get_language_code()},' \
                 f'{alts}, {bool(configuration.get_phrases())},' \
                 f'{configuration.get_boost()}, {ref_total_word_count}, {ref_error_count}, {word_error_rate}, {nlp_model.get_apply_stemming()},' \
                 f'{nlp_model.get_remove_stop_words()}, {nlp_model.get_n2w()}, {nlp_model.get_expand_contractions()}, {ins}, {deletions}, {subs}, ' \
                 f'{deleted_words}, {inserted_words}, {substitute_words}\n'
        with open(full_path, 'a+',) as file:
            try:
                file.write(string)
            except IOError as i:
                print(f'Can not update csv file: {i}')
        print(f'UPDATED: {full_path}')


    def write_html_diagnostic(self, wer_obj, unique_root, result_path):
        aligned_html = '<br>'.join(wer_obj.aligned_htmls)

        result_file = unique_root + '.html'
        write_path = f'{result_path}/{result_file}'
        with open(write_path, 'w') as f:
            try:
                f.write(aligned_html)
            except IOError as i:
                print(f'Can not write html diagnostic {write_path}: {i}')
        print(f'WROTE: diagnostic file: {write_path} ')

    def write_queue_file(self, data):
        try:
            with open(self._queue_file_name, 'a+') as f:
                if isinstance(data, str):
                    info = data.split()
                else:
                    info = data
                for item in info:
                    f.write(item + ',')
        except IOError as e:
            print(f'Can not write diagnostic file: {e}')


    def read_queue_file(self):
        result = None
        try:
            with open(self._queue_file_name, 'r') as f:
                result = f.read()
        except IOError as e:
            print(f'Can not read queue file: {e}')
        except FileNotFoundError as x:
            print(f'Queue file not found: {x}')
        if not result:
            raise IOError('No contents found in queue')
        return result

    def write_hyp(self, file_name, text):
        import os.path

        if not os.path.exists(self.get_result_path()):
            os.makedirs(self.get_result_path())

        p = f'{self.get_result_path()}/{file_name}'

        with open(p, 'w+') as f:
            f.write(text)
