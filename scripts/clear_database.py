from engine.models import *

print ("Deleting QuestionsEntityGroup")
QuestionsEntityGroup.objects.all().delete()

print ("Deleting EntityType")
EntityType.objects.all().delete()

print ("Deleting Choices")
Choices.objects.all().delete()

print ("Deleting Tree")
Tree.objects.all().delete()

print ("Deleting Mapper")
Mapper.objects.all().delete()

print ("Deleting Sentences")
Sentences.objects.all().delete()


print ("Deleting GoodWords")
GoodWords.objects.all().delete()

print ("Deleting Bigrams")
Bigrams.objects.all().delete()

print ("Deleting Intent")
Intent.objects.all().delete()


print ("Deleting ParentSentences")
ParentSentences.objects.all().delete()

print ("Deleting WordMapper")
WordMapper.objects.all().delete()

print ("Deleting Profile")
Profile.objects.all().delete()

print ("Deleting QueryCnt")
QueryCnt.objects.all().delete()

print ("Deleting Variables")
Variables.objects.all().delete()

print ("Deleting KnowledgeBase")
KnowledgeBase.objects.all().delete()

print ("Deleting FeedbackGeneral")
FeedbackGeneral.objects.all().delete()

print ("Deleting Query")
Query.objects.all().delete()

print ("Deleting AnalyticsCount")
AnalyticsCount.objects.all().delete()

print ("Deleting IsTypableData")
IsTypableData.objects.all().delete()


print ("Deleting QueryList")
QueryList.objects.all().delete()


print ("Deleting FeedbackQuery")
FeedbackQuery.objects.all().delete()


print ("Deleting KnowledgeBase2")
KnowledgeBase2.objects.all().delete()


print ("Deleting PcId")
PcId.objects.all().delete()


print ("Deleting ValueExtracter")
ValueExtracter.objects.all().delete()

print ("Deleting FileStorage")
FileStorage.objects.all().delete()

print ("Deleting Leads")
Leads.objects.all().delete()

print ("Deleting FAQModel")
FAQModel.objects.all().delete()

print ("Deleting ProducModel")
ProductModel.objects.all().delete()
