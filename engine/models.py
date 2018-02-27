from django.db import models
from .constants import *
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from ckeditor.fields import RichTextField
from django.utils.safestring import mark_safe

# Create your models here.

class Bigrams(models.Model):
    word1 = models.CharField(max_length=100,
                             null=False,
                             blank=False)
    word2 = models.CharField(max_length=100,
                             null=False,
                             blank=False)
    cnt = models.IntegerField(default=0)

    def __str__(self):
        return self.word1 + " " + self.word2 + " " + str(self.cnt)

#---------------------------------------------------------------------------------

class AnalyticCount(models.Model):
    intent = models.ForeignKey('Intent',
                               null=True,
                               blank=True,
                               on_delete=models.CASCADE)
    entity = models.ForeignKey('Entities',
                               null=True,
                               blank=True,
                               on_delete=models.CASCADE)
    time = models.DateField(auto_now=True)

    def __str__(self):
        return str(self.time)


class Language(models.Model):
    name = models.CharField(max_length=100,
                            null=True,
                            blank=True,
                            default="eng")

    def __str__(self):
        return self.name


class Channel(models.Model):
    name = models.CharField(max_length=100,
                            null=True,
                            blank=True,
                            default="web")

    def __str__(self):
        return self.name


class ChannelSentences(models.Model):
    group_of_sentences = models.ManyToManyField('Sentences',
                                                blank=True)

    name = models.CharField(max_length=100,
                            null=True,
                            blank=True)

    def __str__(self):
        return mark_safe(self.group_of_sentences.all()[0].sentence)

    class Meta:
        ordering = ('-pk',)
        verbose_name = 'dev - Channel Sentences'
        verbose_name_plural = 'dev - Channel Sentences'


class Sentences(models.Model):
    sentence = RichTextField(config_name='default')
    language = models.ForeignKey('Language',
                                 null=True,
                                 blank=True,
                                 on_delete=models.CASCADE)
    channel = models.ForeignKey('Channel',
                                null=True,
                                blank=True,
                                on_delete=models.CASCADE)
    file = models.ForeignKey('Files',
                             null=True,
                             blank=True,
                             on_delete=models.CASCADE)

    def __str__(self):
        return mark_safe(self.sentence)

    class Meta:
        ordering = ('-pk',)
        verbose_name = 'dev - Sentences'
        verbose_name_plural = 'dev - Sentences'


class AutoCorrectWordList(models.Model):
    word = models.CharField(max_length=100,
                            null=False,
                            blank=False)

    def __str__(self):
        return self.word

    class Meta:
        verbose_name = 'dev - Autocorrect Word List'
        verbose_name_plural = 'dev - Autocorrect Word List'

class FeedbackGeneral(models.Model):

    feedback = models.TextField(null=False,
                                blank=False)

    user_id = models.CharField(max_length=100,
                               null=True,
                               blank=False)

    def __str__(self):
        return self.feedback

    class Meta:
        verbose_name = 'debug - Feedback'
        verbose_name_plural = 'debug - Feedbacks'

class QueryFeedbackCounter(models.Model):
    user = models.ForeignKey('Profile',
                             null=True,
                             blank=True,
                             on_delete=models.CASCADE)
    query = models.ForeignKey('QueryCnt',
                              null=True,
                              blank=True,
                              on_delete=models.CASCADE)

    like_cnt = models.IntegerField(default=0)

    dislike_cnt = models.IntegerField(default=0)

    def __str__(self):
        return self.user.user_id + " " + self.query.query + " " + str(self.like_cnt) + " " + str(
            self.dislike_cnt)

    class Meta:
        verbose_name = 'debug - Query Feedback'
        verbose_name_plural = 'debug - Query Feedback'


class Variables(models.Model):
    variable_name = models.TextField(null=False,
                                     blank=False)

    variable_value = models.TextField(null=False,
                                      blank=False)

    def __str__(self):
        return self.variable_name + " " + self.variable_value


class Config(models.Model):
    question_not_recognized = models.TextField(
        default=('I\'m sorry, you can ask me things like...'))
    recommended_queries_statement = models.TextField(
        default=('I\'m sorry, did you wish to mean')
    )
    entry_not_present_in_database = models.TextField(
        default=('Sorry, we could not find the corresponding entry in the records.')
    )
    cancel_button_message = models.TextField(
        default='Hello, what would you like to know about?',
    )
    custom_stop_word = models.TextField(
        default='tell,what,is',
    )
    email_id = models.TextField(
        default='harshdalal442@gmail.com',
    )
    initial_message = models.TextField(
        default='harshdalal442@gmail.com',
    )
    base_response_1 = models.TextField(
        default='harshdalal442@gmail.com',
        null=True,
        blank=True,
    )
    base_response_2 = models.TextField(
        default='harshdalal442@gmail.com',
        null=True,
        blank=True,
    )
    base_response_3 = models.TextField(
        default='harshdalal442@gmail.com',
        null=True,
        blank=True,
    )
    base_response_4 = models.TextField(
        default='harshdalal442@gmail.com',
        null=True,
        blank=True,
    )
    base_response_5 = models.TextField(
        default='harshdalal442@gmail.com',
        null=True,
        blank=True,
    )

    entities_enable = models.BooleanField(default=False)
    intents_enabled = models.BooleanField(default=False)
    entities_group_enabled = models.BooleanField(default=False)
    question_entities_group_enabled = models.BooleanField(default=False)
    trees_enabled = models.BooleanField(default=False)
    word_mappers_enabled = models.BooleanField(default=False)
    mappers_enabled = models.BooleanField(default=False)
    sentences_enabled = models.BooleanField(default=False)
    good_words_enabled = models.BooleanField(default=False)
    bigrams_enabled = models.BooleanField(default=False)
    parent_sentences_enabled = models.BooleanField(default=False)
    profile_enabled = models.BooleanField(default=False)
    query_cnt_enabled = models.BooleanField(default=False)
    variables_enabled = models.BooleanField(default=False)
    knowledgebase_enabled = models.BooleanField(default=False)
    feedback_general_enabled = models.BooleanField(default=False)
    query_enabled = models.BooleanField(default=False)
    analytics_cnt_enabled = models.BooleanField(default=False)
    is_typable_data = models.BooleanField(default=False)
    query_list_enabled = models.BooleanField(default=False)
    feedback_query_enabled = models.BooleanField(default=False)
    config_enabled = models.BooleanField(default=False)
    knowledgebase2_enabled = models.BooleanField(default=False)
    pc_id_enabled = models.BooleanField(default=False)
    value_extracter_enabled = models.BooleanField(default=False)
    file_storage = models.BooleanField(default=False)

    def __str__(self):
        return 'Config'


class Entities(models.Model):
    entity_name = models.TextField(blank=False,
                                   null=False)

    keywords = models.TextField(default='',
                                blank=True,
                                null=False,
                                help_text=("The keywords sets should be "
                                           "comma separated and the keywords "

                                           "should be space separated"))
    parent = models.ForeignKey("self",
                               null=True,
                               blank=True,
                               on_delete=models.CASCADE)

    def __str__(self):
        return self.entity_name

    def get_keywords(self):
        keywords = list()
        keyword_sets = self.keywords.lower().split(',')

        for keyword_set in keyword_sets:
            keywords.append([keyword.strip()
                             for keyword in keyword_set.split(' ')])

        return keywords

    def is_this_entity(self, sentence):
        words = sentence.split()
        keyword_sets = self.get_keywords()

        for keyword_set in keyword_sets:

            keyword_set_present = True
            for keyword in keyword_set:
                if not keyword in words:
                    keyword_set_present = False
                    break
            if keyword_set_present:
                return True
        return False

    class Meta:
        verbose_name = 'dev - Entity'
        verbose_name_plural = 'dev - Entities'


class DataValidators(models.Model):
    function = models.TextField(default='',
                                null=True,
                                blank=True)

    entity_type = models.ForeignKey('EntityGroup',
                                    blank=True,
                                    null=True,
                                    on_delete=models.CASCADE)

    def __str__(self):
        return self.function

    class Meta:
        verbose_name = 'dev - Data Validators'
        verbose_name_plural = 'dev - Data Validators'


class Data(models.Model):
    entity_name = models.CharField(max_length=100,
                                   null=False,
                                   blank=False)

    entity_value = models.CharField(max_length=100,
                                    null=False,
                                    blank=False)

    user = models.ForeignKey('Profile',
                             null=True,
                             blank=True,
                             on_delete=models.CASCADE)

    current_stage = models.CharField(max_length=100,
                                     null=True,
                                     blank=True)

    redirect_intent = models.TextField(null=True,
                                       blank=True)

    redirect_entities_delete = models.TextField(null=True,
                                                blank=True)
    cnt = models.IntegerField(default=1)

    class Meta:
        verbose_name = 'debug - Data'
        verbose_name_plural = 'debug - Data'

    def __str__(self):
        return self.entity_name + " " + self.entity_value


class Recommendation(models.Model):
    query = models.CharField(max_length=100,
                             null=False,
                             blank=False)
    entity = models.ForeignKey('Entities',
                               on_delete=models.CASCADE)
    intent = models.ForeignKey('Intent',
                               on_delete=models.CASCADE)

    def __str__(self):
        return self.query

    class Meta:
        verbose_name = 'dev - Recommendation'
        verbose_name_plural = 'dev - Recommendations'

class Files(models.Model):
    file_name = models.CharField(max_length=100,
                                 null=True,
                                 blank=True)

    file = models.FileField(upload_to='files/')

    def __str__(self):
        return self.file_name

    class Meta:
        verbose_name = 'file - Files'
        verbose_name_plural = 'file - Files'


class QuestionsEntityGroup(models.Model):
    name = models.TextField(null=True,
                            blank=True)
    entity_group = models.ForeignKey('EntityGroup',
                                     on_delete=models.CASCADE,
                                     related_name="question_group_set")
    question = models.ForeignKey(Sentences,
                                 blank=True,
                                 null=True,
                                 on_delete=models.CASCADE,
                                 related_name='question_entitytype',
                                 help_text='This is the question to be asked in the flow.')
    re_question = models.ForeignKey(Sentences,
                                    blank=True,
                                    null=True,
                                    on_delete=models.CASCADE,
                                    related_name='re_question_entitytype',
                                    help_text='This is the question to be asked when user enters an invalid query.')
    intent_on_click = models.TextField(null=True,
                                       blank=True)
    entity_to_delete = models.TextField(null=True,
                                        blank=True,
                                        help_text='Please enter different entities seperated by space which are to be deleted')
    class Meta:
        verbose_name = 'dev - QuestionEntityGroup'
        verbose_name_plural = 'dev - QuestionEntityGroup'

    def __str__(self):
        return self.name


class EntityGroup(models.Model):
    name = models.CharField(max_length=100,
                            null=False,
                            blank=False)

    choices = models.ManyToManyField(Entities,
                                     blank=True,
                                     related_name="entity_choices")

    is_clickable = models.BooleanField(default=True)
    is_typable = models.BooleanField(default=False)
    is_primary = models.BooleanField(default=False)
    is_persistent = models.BooleanField(default=False)
    is_loop = models.BooleanField(default=False)

    is_date = models.BooleanField(default=False)
    is_dropdown = models.BooleanField(default=False)
    is_file = models.BooleanField(default=False)
    multi = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'dev - EntityGroup'
        verbose_name_plural = 'dev - EntityGroup'


class ProductModel(models.Model):
    product_name = models.CharField(max_length=100,
                                    null=True,
                                    blank=True)

    class Meta:
        verbose_name = 'Help - Product'
        verbose_name_plural = 'Help - Products'


class FAQModel(models.Model):
    question = models.CharField(max_length=100,
                                null=True,
                                blank=True)
    answer = models.CharField(max_length=100,
                              null=True,
                              blank=True)
    product = models.ForeignKey(ProductModel,
                                on_delete=models.CASCADE,
                                null=True,
                                blank=True)
    date = models.DateField(auto_now=True)
    faq_status = models.CharField(max_length=20,
                                  choices=FAQ_CHOICES,
                                  null=True,
                                  blank=True,
                                  default='Not added')

    def __str__(self):
        return self.question

    class Meta:
        verbose_name = 'help - FAQ'
        verbose_name_plural = 'help - FAQs'


class Leads(models.Model):
    name = models.CharField(max_length=100,
                            null=True,
                            blank=True)
    zip_code = models.CharField(max_length=100,
                                null=True,
                                blank=True)
    mob_no = models.CharField(max_length=100,
                              null=True,
                              blank=True)
    product = models.ForeignKey(ProductModel,
                                on_delete=models.CASCADE)
    date = models.DateField(auto_now=True)
    is_exported = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'help - Leads'
        verbose_name_plural = 'help - Leads'


class Tree(models.Model):
    name = models.TextField(null=True,
                            blank=True)
    question_entity_type = models.ForeignKey(QuestionsEntityGroup,
                                             blank=True,
                                             null=True,
                                             on_delete=models.CASCADE)
    answer = models.ForeignKey(ChannelSentences,
                               blank=True,
                               null=True,
                               related_name='tree_answer',
                               on_delete=models.CASCADE)
    mapper = models.ManyToManyField('Mapper',
                                    blank=True,
                                    related_name='mappers')
    current_stage = models.TextField(null=True,
                                     blank=True)
    is_diversify = models.BooleanField(default=False)
    is_tree_mapper_create = models.BooleanField(default=True)
    is_fixed = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'dev - Tree'
        verbose_name_plural = 'dev - Tree'


class Intent(models.Model):
    name = models.CharField(max_length=100,
                            null=False,
                            blank=False)
    keywords = models.TextField(default='',
                                blank=False,
                                null=False,
                                help_text=("The keywords sets should be "
                                           "comma separated and the keywords "
                                           "should be space separated"))
    restricted_keywords = models.TextField(default='',
                                           blank=True,
                                           null=True,
                                           help_text=("The keywords sets should be "
                                                      "comma separated and the keywords "
                                                      "should be space separated"))
    tree = models.ForeignKey(Tree,
                             null=True,
                             blank=True,
                             related_name="intent_set",
                             on_delete=models.CASCADE)
    answer = RichTextField(config_name='default',
                           null=True,
                           blank=True)
    level = models.IntegerField(default=1)

    def __str__(self):
        return self.name

    def get_keywords(self):
        keywords = list()
        keyword_sets = self.keywords.lower().split(',')

        for keyword_set in keyword_sets:
            keywords.append([keyword.strip()
                             for keyword in keyword_set.split(' ')])

        return keywords

    def get_bad_keywords(self):
        keywords = list()
        keyword_sets = self.restricted_keywords.lower().split(',')

        for keyword_set in keyword_sets:
            keywords.append([keyword.strip()
                             for keyword in keyword_set.split(' ')])

        return keywords

    def is_this_intent(self, sentence):
        words = sentence.split()
        keyword_sets = self.get_keywords()
        restricted_keyword_sets = self.get_bad_keywords()

        bool_keyword_present = False
        bool_restricted_keyword_present = False

        for keyword_set in keyword_sets:
            keyword_set_present = True
            for keyword in keyword_set:
                if not keyword in words:
                    keyword_set_present = False
                    break
            if keyword_set_present:
                bool_keyword_present = True

        for keyword_set in restricted_keyword_sets:
            keyword_set_present = True
            for keyword in keyword_set:
                if not keyword in words:
                    keyword_set_present = False
                    break
            if keyword_set_present:
                bool_restricted_keyword_present = True

        if bool_keyword_present == True and bool_restricted_keyword_present == False:
            return True
        return False

    class Meta:
        verbose_name = 'dev - Intent'
        verbose_name_plural = 'dev - Intents'


class Mapper(models.Model):
    entity = models.ForeignKey(Entities,
                               on_delete=models.CASCADE,
                               null=True,
                               blank=True)
    next_tree = models.ForeignKey('Tree',
                                  null=True,
                                  blank=True,
                                  related_name='tree_mapper',
                                  on_delete=models.CASCADE)
    name = models.CharField(max_length=100,
                            null=True,
                            blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Mapper'
        verbose_name_plural = 'Mappers'


class QueryCnt(models.Model):
    query = models.CharField(max_length=100,
                             null=True,
                             blank=True)
    count = models.IntegerField(default=0)
    language = models.ForeignKey('Language',
                                 null=True,
                                 blank=True,
                                 on_delete=models.CASCADE)
    channel = models.ForeignKey('Channel',
                                null=True,
                                blank=True,
                                on_delete=models.CASCADE)

    def __str__(self):
        return self.query


class UniqueUsers(models.Model):
    user_id = models.CharField(max_length=100,
                               null=False,
                               blank=False)

    time = models.DateField(auto_now=True)

    def __str__(self):
        return self.user_id


class Profile(models.Model):
    user_id = models.CharField(max_length=500,
                               null=True,
                               blank=False)
    tree = models.ForeignKey(Tree,
                             null=True,
                             blank=True,
                             on_delete=models.CASCADE)
    current_intent = models.ForeignKey(Intent,
                                       null=True,
                                       blank=True,
                                       on_delete=models.CASCADE)
    current_entity = models.ForeignKey(Entities,
                                       null=True,
                                       blank=True,
                                       on_delete=models.CASCADE)
    current_query = models.CharField(max_length=100,
                                     null=True,
                                     blank=True)
    re_question = models.BooleanField(default=False)
    stage = models.TextField(null=True,
                             blank=True,
                             default="pre")

    def __str__(self):
        return self.user_id

    class Meta:
        verbose_name = 'debug - Profile'
        verbose_name_plural = 'debug - Profile'


class Log(models.Model):
    query = models.CharField(max_length=100,
                             null=True,
                             blank=True)
    time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(Profile,
                             related_name='Profile2',
                             on_delete=models.CASCADE)
    language = models.ForeignKey('Language',
                                 null=True,
                                 blank=True,
                                 on_delete=models.CASCADE)
    channel = models.ForeignKey('Channel',
                                null=True,
                                blank=True,
                                on_delete=models.CASCADE)
    answer_succesfull = models.BooleanField(default=False)
    chatbot_answer = models.CharField(max_length=100,
                                      null=True,
                                      blank=True)
    clicked = models.BooleanField(default=False)

    def __str__(self):
        return self.query + str(self.time)

    class Meta:
        verbose_name = 'debug - Log'
        verbose_name_plural = 'debug - Logs'


class WordMapper(models.Model):
    keyword = models.CharField(max_length=100,
                               default='',
                               null=True,
                               blank=True,
                               unique=True)

    similar_words = models.TextField(default='',
                                     blank=False,
                                     null=False)

    def get_similar_words(self):
        return [word.strip() for word in self.similar_words.split(',')]

    def __str__(self):
        return self.keyword

    class Meta:
        verbose_name = 'dev - WordMapper'
        verbose_name_plural = 'dev - WordMappers'


def load_dictionary():
    words = set()
    WORD_MAP = {}
    word_mappers = WordMapper.objects.all()
    for word_mapper in word_mappers:
        for similar_word in word_mapper.get_similar_words():
            WORD_MAP[similar_word] = word_mapper.keyword

    for word in WORD_MAP:
        if word != '':
            words.add(word)
        if WORD_MAP[word] != '':
            words.add(WORD_MAP[word])

    intents = Intent.objects.all()
    for intent in intents:
        keywords = [item for sublist in intent.get_keywords()
                    for item in sublist]
        for keyword in keywords:
            if keyword != '':
                words.add(keyword)

    entities = Entities.objects.all()
    for entity in entities:
        keyword_sets = entity.get_keywords()
        for keyword_set in keyword_sets:
            for keyword in keyword_set:
                words.add(keyword)

    f = open(DICTIONARY_FILE, 'r+')
    f.truncate()

    for word in words:
        f.write(word.lower() + '\n')
    f.close()


# @receiver(post_save, sender=Data, dispatch_uid="update_data_count")
# def update_data(sender, instance, created, **kwargs):
#     if instance.entity_name != instance.entity_name.lower():
#         instance.entity_name = instance.entity_name.lower()
#         instance.save()


# @receiver(post_save, sender=Variables, dispatch_uid="update_variable_count")
# def update_variable(sender, instance, created, **kwargs):
#     if instance.variable_name != instance.variable_name.lower():
#         instance.variable_name = instance.variable_name.lower()
#         instance.save()
#

@receiver(post_save, sender=Entities, dispatch_uid="update_entity_count")
def update_entities(sender, instance, created, **kwargs):
    keywords = list()
    keyword_sets = instance.keywords.lower().split(',')

    for keyword_set in keyword_sets:
        keywords.append([keyword.strip()
                         for keyword in keyword_set.split(' ')])

    for word in keywords:
        for small_word in word:
            try:
                AutoCorrectWordList.objects.get(word=small_word)
            except:
                AutoCorrectWordList(word=small_word).save()


@receiver(post_save, sender=Intent, dispatch_uid="update_intent_count")
def update_intent(sender, instance, created, **kwargs):
    keywords = list()
    keyword_sets = instance.keywords.lower().split(',')

    for keyword_set in keyword_sets:
        keywords.append([keyword.strip()
                         for keyword in keyword_set.split(' ')])

    for word in keywords:
        for small_word in word:
            try:
                AutoCorrectWordList.objects.get(word=small_word)
            except:
                AutoCorrectWordList(word=small_word).save()

    if created == True:
        x = instance.answer.replace(" ", "")
        if x != "":
            s = Sentences(sentence=instance.answer)
            s.save()
            intent_name = instance.name
            tree_name = intent_name + ".Tree"
            tree = Tree(name=tree_name)
            tree.save()
            tree.answer = ChannelSentences.objects.get(name=instance.answer)
            tree.save()
            instance.tree = tree
            instance.save()
        else:
            intent_name = instance.name
            tree_name = intent_name + ".Tree"
            tree = Tree(name=tree_name)
            tree.save()
            instance.tree = tree
            instance.save()


# This 4 lines are magical, p.s. do not remove this ;)
def on_transaction_commit(func):
    def inner(*args, **kwargs):
        transaction.on_commit(lambda: func(*args, **kwargs))

    return inner


@receiver(post_save, sender=Sentences, dispatch_uid="update_sentence_count")
def update_sentence(sender, instance, created, **kwargs):
    keywords = instance.sentence.lower().split(" ")
    for word in keywords:
        word = word.strip()
        word = word.replace("<p>","")
        word = word.replace("</p>", "")
        word = word.replace("&nbsp;", "")
        word = word.replace(".", "")
        try:
            AutoCorrectWordList.objects.get(word=word)
        except:
            AutoCorrectWordList(word=word).save()

    if created:
        a = ChannelSentences(name=instance.sentence)
        a.save()
        a.group_of_sentences.add(instance)


@receiver(post_save, sender=Tree, dispatch_uid="update_tree_count")
@on_transaction_commit
def update_tree(sender, instance, **kwargs):
    #   print("IN TREE POST_SAVE -----------------------------------------------------------------------------------------------------------------------------------")
    if instance.is_tree_mapper_create:
        if instance.question_entity_type:
            intent = instance.intent_set.all()
            intent_name = ""
            if intent.count() > 0:
                intent_name = intent[0].name
            else:
                intent_name = instance.name[:-5]

            entityType = instance.question_entity_type.entity_group
            choices = entityType.choices.all()
            str = intent_name + '.' + entityType.name + '.'

            list = []

            print(len(choices), "choicessssssssssssssssssssssss")

            if (len(choices) == 0):
                treee = Tree.objects.filter(name=str + "null.Tree")
                if treee.count() == 0:
                    teee = Tree(name=str + "null.Tree")
                    teee.save()
            else:
                if instance.is_diversify:
                    for choice in choices:
                        list.append(choice.entity_name)
                        treee = Tree.objects.filter(name=str + list[0] + ".Tree")
                        if treee.count() == 0:
                            teee = Tree(name=str + list[0] + ".Tree")
                            teee.save()
                        list.pop()
                else:
                    treee = Tree.objects.filter(name=str + "General" + ".Tree")
                    if treee.count() == 0:
                        print("Goes to save ---- GEnereal")
                        tee = Tree(name=str + "General" + ".Tree")
                        tee.save()

            mapper_list = []

            if (len(choices) == 0):
                tree = Tree.objects.filter(name=str + "null.Tree").get()
                print("Tree: ----------", tree)
                c = Entities.objects.get(entity_name="null")
                print(c)
                mapy = Mapper(entity=c,
                              next_tree=tree,
                              name=str + "null")
                mapy.save()
                mapper_list.append(mapy)
            else:
                if instance.is_diversify:
                    for choice in choices:
                        list.append(choice.entity_name)
                        tree = Tree.objects.filter(
                            name=str + list[0] + ".Tree").get()
                        mapy = Mapper(entity=choice,
                                      next_tree=tree,
                                      name=str + list[0])
                        mapy.save()
                        mapper_list.append(mapy)
                        list.pop()
                else:
                    for choice in choices:
                        list.append(choice.entity_name)
                        tree = Tree.objects.filter(
                            name=str + "General" + ".Tree").get()
                        mapy = Mapper(entity=choice,
                                      next_tree=tree,
                                      name=str + list[0])
                        mapy.save()
                        mapper_list.append(mapy)
                        list.pop()

            print("EEXECUTING ------------------------------------------------------------------------------------")
            for mapp in mapper_list:
                print(mapp, type(mapp))
                instance.mapper.add(mapp)
