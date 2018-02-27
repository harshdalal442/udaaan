from django.contrib import admin
from django.contrib.auth.models import Group, User
from import_export import resources
#from django.engine.models import *
from import_export.admin import ImportExportModelAdmin

from .constants import LISTS_PER_PAGE
from .models import *
from .utils import get_entity, get_intent
from .views import do_pre_processing


class ConfigAdmin(admin.ModelAdmin):
   def has_delete_permission(self, request, obj=None):
       return False
   def has_add_permission(self, request):
       return False

class QuestionEntityGroupAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return True

    def get_model_perms(self, request):
        if not Config.objects.all()[0].question_entities_group_enabled:
            return {}
        else:
            return {
                'add': self.has_add_permission(request),
                'change': self.has_change_permission(request),
                'delete': self.has_delete_permission(request),
            }

class EntityGroupAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return True

    def get_model_perms(self, request):
        if not Config.objects.all()[0].entities_group_enabled:
            return {}
        else:
            return {
                'add': self.has_add_permission(request),
                'change': self.has_change_permission(request),
                'delete': self.has_delete_permission(request),
            }

class EntitiesAdmin(admin.ModelAdmin):
    list_display = ('entity_name', 'keywords', 'parent', )

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return True

    def get_model_perms(self, request):
        if not Config.objects.all()[0].entities_enable:
            return {}
        else:
            return {
                'add': self.has_add_permission(request),
                'change': self.has_change_permission(request),
                'delete': self.has_delete_permission(request),
            }

class SentencesAdmin(admin.ModelAdmin):
    list_per_page = LISTS_PER_PAGE

class TreeAdmin(admin.ModelAdmin):
    list_display = ('name','question_entity_type','current_stage')
    #exclude = ('is_fixed','is_tree_mapper_create')
    #list_filter = ('question_entity_type__entity_group__name',)
    list_per_page = LISTS_PER_PAGE

    def return_answer(self,obj):
        if obj.answer is not None:
            return obj.answer
        else:
            return ''
    def has_delete_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return True

    def get_model_perms(self, request):
        if not Config.objects.all()[0].trees_enabled:
            return {}
        else:
            return {
                'add': self.has_add_permission(request),
                'change': self.has_change_permission(request),
                'delete': self.has_delete_permission(request),
            }

class QueryAdmin(admin.ModelAdmin):
    list_display = ('query', 'get_preprocessed_question', 'get_intent_question', 'get_entity_question', 'chatbot_answer', 'answer_succesfull', 'clicked', 'time')
    list_filter = ('time', 'answer_succesfull', 'clicked', )

    def get_preprocessed_question(self, obj):
        return do_pre_processing(obj.query,"web","eng")

    def get_intent_question(self, obj):
        return get_intent(do_pre_processing(obj.query,"web","eng"))

    def get_entity_question(self, obj):
        return get_entity(do_pre_processing(obj.query,"web","eng"))

class IntentResource(resources.ModelResource):
    class Meta:
        model = Intent
        fields = ('id','name','keywords')

class DataAdmin(admin.ModelAdmin):
    list_display = ('entity_name','entity_value','user')
#
# class HSBCChequeResource(resources.ModelResource):
#     class Meta:
#         model = HSBCChequeModel
#         fields = ('id','cheque_number','deposit_slip_number','amount','status','bank_branch')
#
# class HSBCTransactionResource(resources.ModelResource):
#     class Meta:
#         model = HSBCTransactionModel

# class IntentResource(ImportExportModelAdmin):
#     pass
class IntentAdmin(admin.ModelAdmin):
    #resource_class = IntentResource
    #exclude=('tree',)
    list_display = ('name', 'get_keywords', 'level', )
    # list_filter = ('level', )
    list_per_page = LISTS_PER_PAGE
    def get_keywords(self, obj):
        return ', '.join(obj.keywords.split(','))
#   
# class HSBCTransactionAdmin(ImportExportModelAdmin):
#     resource_class = HSBCTransactionResource
#
# class HSBCChequeAdmin(ImportExportModelAdmin):
#     resource_class = HSBCChequeResource

class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'answer', 'faq_status', )
    list_filter = ('faq_status', )
    pass

class WordMapperAdmin(admin.ModelAdmin):
    list_display = ('keyword', 'get_similar_words', )

    def get_keywords(self, obj):
        return ', '.join(self.similar_words.split(','))


class ParentSentencesAdmin(admin.ModelAdmin):
    # list_display = ('get_answer', )
    #
    # def get_answer(self, obj):
    #     return obj.answer_sentence.all()[0]
    pass
# Unregister your models here.
admin.site.unregister(Group)
admin.site.unregister(User)

# Register your models here.
admin.site.register(Config, ConfigAdmin)
admin.site.register(QuestionsEntityGroup, QuestionEntityGroupAdmin)
admin.site.register(EntityGroup, EntityGroupAdmin)
admin.site.register(Entities, EntitiesAdmin)
admin.site.register(Sentences, SentencesAdmin)
admin.site.register(Tree, TreeAdmin)
admin.site.register(Log, QueryAdmin)
admin.site.register(Intent, IntentAdmin)
admin.site.register(FAQModel, FAQAdmin)
admin.site.register(WordMapper, WordMapperAdmin)
admin.site.register(ChannelSentences, ParentSentencesAdmin)
admin.site.register(Data, DataAdmin)

admin.site.register(Mapper)
admin.site.register(AutoCorrectWordList)
admin.site.register(Profile)
admin.site.register(QueryCnt)
admin.site.register(Variables)
admin.site.register(AnalyticCount)
admin.site.register(Recommendation)
admin.site.register(QueryFeedbackCounter)
admin.site.register(DataValidators)
admin.site.register(Files)
admin.site.register(Leads)
admin.site.register(ProductModel)
admin.site.register(Language)
admin.site.register(Channel)
admin.site.register(UniqueUsers)