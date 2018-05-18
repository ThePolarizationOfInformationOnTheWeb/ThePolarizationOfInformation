# ThePolarizationOfInformationOnTheWeb
Across the internet, how polarized are opinions and information covering a topic?

## -Objective-
 Understanding and developing a more accurate model of modern day information aggregation is the primary goal of this study. Specifically we aim to answer the question: Across the internet, how polarized are opinions and information covering a topic? 
 
## -Approach- 
 Consider many users browsing the internet researching a controversial topic. Depending on their predispositions, one would begin their inquiry by choosing a familiar news portal. Then these sites would link to other news sites, blogs, etc. which a user will follow with a probability that reflects their current state of opinion. As described, users follow certain strains of information with higher probability, becoming confined to certain sections of the internet. This explanation implies that the way information is accessed on the web is a slow mixing Markov process, which would correlate with a polarization of opinion in the society. 
 Different users with biases can be identified by the states of the Markov process they are in. Then the polarization of information surrounding a topic can be characterized by the mixing rate among the ensemble of different users. We can summarize our approach with the following question: how much common information should different users see before they begin to agree? 
 
## -Data-
 For this study we will be working with data from the web, that is any information that is accessible by a conventional user investigating a topic. For example we will see: articles, blog posts, tweets, etc.
 
 The first challenge we face with this data is determining what information would indeed be relevant to influencing a user's opinion regarding a topic. Then, once this document is deemed relevant, another question we must answer is: Where on the spectrum of positions we are considering in our model does the relevant document lie? To better understand the issue consider a simple solution of labeling documents based on the presence or absence of controversial keywords and phrases.
 
 To develop techniques to resolve the complexities described above, we can first harvest data from the web by developing an unbiased web crawler. Then we may begin our data analysis to come up with heuristics that will provide satisfactory solutions. 
 
## -Impact-
 An understanding of the polarization of information on the web could be used to help policy makers identify topics of controversy or agreement to better serve their constituents. Another impact is in personalizing search suggestions that can break users out of confined regions of the internet.
