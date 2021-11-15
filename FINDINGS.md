Findings:

Initial method simply returned the first sentence found in any article. By default, this happened to be the first sentence in article 109, ``Bird migration is the regular seasonal movement, often north and south along a flyway, between breeding and wintering grounds.'' We counted number of times the article was correctly identified, and number of times the provided answer appeared in the sentence. Interestingly, because the terms ``north'' and ``south'' are answers to two unrelated questions, this method counted those as correct. Another question asked something similar, ``What is the most common directionof migration in autumn?''; the provided answer ``south'' appears in the provided answer. The last question was looking for this precise sentence; it is good to know that this method will correctly detect this correct answer. In the set of questions, 89 are for this article, so those are correct by default.

BadAnswerer: Of 2505 total questions, the correct article was found 89 times and the correct sentence was found 4 times.

Next method simply used RAKE keyword search. Of 2505 questions, got 1453 correct articles and 769 correct sentences.

KeywordAnswerer: Of 2505 total questions, the correct article was found 1453 times and the correct sentence was found 769 times.
