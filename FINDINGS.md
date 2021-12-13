Findings:

Initial method simply returned the first sentence found in any article. By default, this happened to be the first sentence in article 109, ``Bird migration is the regular seasonal movement, often north and south along a flyway, between breeding and wintering grounds.'' We counted number of times the article was correctly identified, and number of times the provided answer appeared in the sentence. Interestingly, because the terms ``north'' and ``south'' are answers to two unrelated questions, this method counted those as correct. Another question asked something similar, ``What is the most common directionof migration in autumn?''; the provided answer ``south'' appears in the provided answer. The last question was looking for this precise sentence; it is good to know that this method will correctly detect this correct answer. In the set of questions, 89 are for this article, so those are correct by default.

BadAnswerer: Of 2505 total questions, the correct article was found 89 times and the correct sentence was found 4 times. (0%)

Next method simply used RAKE keyword search. Of 2505 questions, got 1453 correct articles and 769 correct sentences.

KeywordAnswerer: Of 2505 total questions, the correct article was found 1453 times and the correct sentence was found 769 times. (31%)

Next method - broke RAKE keywords into component pieces. For instance, from the question: "On what did Skousen analyze ink and pencil remnants?" we previously found only 2 compound keywords ("skousen analyze ink" "pencil remnants"); now we find 5 ("skousen" "analyze" "ink" "pencil" "remnants")
Of 2505 total questions, the correct article was found 2206 times and the correct sentence was found 1380 times. (55%)

Next method - blacklisting just two words ("one", "type"), which seem to be particular to questions, did not improve results.

While preparing to add NE utiliation, explored how question words are used. There is a list of questions, below, with multiple question words in a single question. Need to use better system (POS tagging? syntatic analysis?)

Some difficulty when trying to find meronyms and holonyms... because it's not quite as simple as that.


*Troublesome questions (section to be cleaned):*
G:\Source\6320_Project\venv\Scripts\python.exe "C:\Program Files\JetBrains\PyCharm 2021.2.2\plugins\python\helpers\pydev\pydevd.py" --multiproc --qt-support=auto --client 127.0.0.1 --port 52510 --file G:/Source/6320_Project/main.py
Connected to pydev debugger (build 212.5284.44)
{'q': 'When mixed wit clay, what is bitumen called?', 'article': 181, 'a': 'asphaltum'}
{'q': 'In what years where phonautograms converted to audible sound?', 'article': 282, 'a': '2000s'}
{'q': 'What happens when frequency decreases in the bass?', 'article': 282, 'a': 'recording amplitude increased'}
{'q': 'How many colors were 45s available in when first released?', 'article': 282, 'a': 'seven colors'}
{'q': 'Who used cognitive science to learn how people understand comics?', 'article': 58, 'a': 'Neil Cohn'}
{'q': 'How were comics published when serialization became less common?', 'article': 58, 'a': 'as albums'}
{'q': 'What was the issue date when this superhero team debuted?', 'article': 220, 'a': 'Nov. 1961'}
{'q': 'In what city was Marvel based when it was founded?', 'article': 220, 'a': 'New York City'}
{'q': 'How old was Mabel when she became deaf?', 'article': 56, 'a': '15'}
{'q': 'Who taught Bell when he was very young?', 'article': 56, 'a': 'father'}
{'q': 'Who was on Cygnet I when it crashed?', 'article': 56, 'a': 'Selfridge'}
{'q': 'Where did the Bells live when the Halifax Explosion happened?', 'article': 56, 'a': 'Beinn Bhreagh'}
{'q': 'What was one reason why the Dominican Order was established?', 'article': 287, 'a': 'to combat heresy'}
{'q': 'What happens when a plant remains totipotent?', 'article': 222, 'a': 'ability to give rise to a new individual plant'}
{'q': 'How far do penguins travel when they migrate?', 'article': 109, 'a': 'over 1,000 km'}
{'q': 'What happens when the site attachment is made?', 'article': 109, 'a': 'they show high site-fidelity'}
{'q': 'What group of people debate when humans stated wearing clothes?', 'article': 196, 'a': 'Scientists'}
{'q': 'When did and how did Aung San pass away ?', 'article': 226, 'a': 'July 1947, political rivals assassinated Aung San'}
{'q': 'What animals where domesticated in Burma for industry use ?', 'article': 226, 'a': 'elephants, which are also tamed or bred in captivity for use as work animals'}
{'q': 'What did parents do when the wages were finally raised?', 'article': 273, 'a': 'send their children to school instead of work'}
{'q': 'What happens when companies outsource?', 'article': 179, 'a': 'somewhat reshapes the industry ecosystem with biotechnology companies'}
{'q': 'What is expected when the relationships are made public?', 'article': 179, 'a': 'relationship between doctors and Pharmaceutical industry will become fully transparent'}
{'q': 'What happens when a childs food is restricted?', 'article': 347, 'a': 'children whose food is restricted have diarrhea of longer duration and recover intestinal function more slowly'}
{'q': "What is the WHO's recipe for ORS?", 'article': 347, 'a': 'one liter water with one teaspoon salt (3 grams) and two tablespoons sugar (18 grams) added'}
{'q': 'What does WHO recommend to do?', 'article': 347, 'a': 'children with diarrhea continue to eat as sufficient nutrients are usually still absorbed to support continued growth and weight gain'}
{'q': 'What does WHO recommend?', 'article': 347, 'a': 'a child with diarrhea continue to be fed'}
{'q': 'What group did the crusaders who attacked Valencia belong to?', 'article': 160, 'a': 'Order of Calatrava'}
{'q': "What where the limitations of Greg's analyses?", 'article': 281, 'a': 'English Renaissance drama'}
Traceback (most recent call last):
  File "G:/Source/6320_Project/main.py", line 251, in <module>
    test()
  File "G:/Source/6320_Project/main.py", line 236, in test
    quest_types(all_questions)
  File "G:/Source/6320_Project/main.py", line 216, in quest_types
    return
KeyboardInterrupt

Process finished with exit code -1073741510 (0xC000013A: interrupted by Ctrl+C)


note that the questions with two wh words, "when" occurs with others most frequently in the non-driving position; "who" the least frequently


Naive checking of named entities in the answer gives poor results. the following questions have the correct answer in the top result, but the associated NE would remove them from consideration:
'Of what was Magadha one of sixteen?'
['one_CARDINAL', 'sixteen_CARDINAL', 'India_GPE']

'Who seized the US Embassy in Iran in 1979?'
['November 4, 1979_DATE', 'the United States Embassy_GPE', '52_CARDINAL', 'the United States_GPE', 'Mohammad Reza Pahlavi_PERSON', 'Iran_GPE']

'What type of government did Espartero have?'
['Maria Cristina_PERSON', 'Espartero_PERSON', 'Spain_GPE', 'two years_DATE', '18th_ORDINAL', '16 September 1840 to_DATE', 'May 1841_DATE']

'On what did Skousen analyze ink and pencil remnants?'
['the Community of Christ—RLDS Church_ORG', 'Independence_GPE', 'Missouri_GPE']

'Who ordered Valencia punished for supporting Charles?'
['25 April 1707_DATE', 'English_NORP', 'Valencia_PERSON', 'Philip_PERSON', 'Valencia_PERSON', 'Charles of_PERSON', 'Austria_GPE']

'What is the natural gas condensate used to dilute bitumen?'
(no named entities)

'When did the Ming hold the divide and rule policy?'
['Luciano Petech_PERSON', 'Sato Hisashi_PERSON', 'Tibet_GPE', 'Sakya_ORG']

'What does an inker do?'
['American_NORP']

'What was a normal play time per side for LPs?'
['up to 30 minutes_TIME', 'about 22 minutes_TIME', 'about forty-five minutes_CARDINAL']

'What is the last step in the stemmatic method?'
(no named entities)


SimpleNE does no better than SimpleKeyword on 100 questions (correct article 90 times; correct sentence 63)
Of 2505 total questions, the correct article was found 2207 times and the correct sentence was found 1380 times.
compared to:
Of 2505 total questions, the correct article was found 2206 times and the correct sentence was found 1380 times. (55%)

When trying to make boxplots based on deltas, we found that the basic keyword answerer gave 15 questions only one result. that could be interesting, right? 