# ThePolarizationOfInformationOnTheWeb
Across the internet, how polarized are opinions and information covering a topic?

## -Objective-
Popular microblogs such as Twitter have become sources of information as well as an incubator for emerging schools of thought. Twitter encourages users to share their opinions and information about current issues and events no matter how contrarian, and access to such a variety of viewpoints has the potential to foster awareness. However, it seems groups of society are forming increasingly polarized opinions leading to disagreements over even factual details. This concerning observation has been a common topic of conversation as of late, but an accepted method for quantifying the polarization between camps on a topic to topic basis has yet to be developed, leaving the dialogue and, as a result, the proposed solutions subjective and diffcult to act upon. 

Our initial focus will be on analyzing the network of information and opinions on Twitter, with the intention of creating a model for quantifying polarization that is scalable and extensible for the inclusion of a variety of types of data, such as news articles and other popular social networks like Facebook. This decision was primarily made to expedite the development of the methodology. Twitter maintains a fantastic API for developers and researchers which provides an easy to use access point for data and useful functionality.
 
## -Approach- 
_Retrieving Relevant Information and Opinions:_ The first task is to collect a sample of sources which are disseminating information about a specific topic within a specified time frame. 

_Modeling the Network:_ Once the relevant sources are sampled, the next task is to build a weighted network summarizing the relations between the tweets. 

_Community Detection:_ The weighted network model of the collected tweets will be input to a community detection algorithm developed in previous work from the University of Hawai’i Big Data Lab (Paravi and Santhanam, 2015).

_Polarity Calculations:_ Lastly, once the network clusters are identified, the final task is to quantify the polarity between the individual communities and among the graph as a whole.
 
## -Impact-
This research will lead to a new way of finding common ideas that exist between polarized groups, and by identifying these common ideas, a bridge of communication can be promoted. By speaking to the ideas that are shared by both groups, users can be broken out of the confined regions of the internet they have found themselves in. Furthermore, politicians may use these commonalities to properly represent their constituents and make bipartisan progress.
