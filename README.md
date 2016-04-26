# GoogleNewsAnalysis using R

We apply Non-negative Matrix Factorization (NMF) on the term-document matrix to discover countries' similar topical interests in news reporting as "themes" . NMF is a matrix factorization technique that is used to transform the term-document matrix into word-themes and theme-documents matrix. The non-negative feature provides the better interpretability from the text . Based on the theme-document matrix obtained from NMF and the documents' source countries, we create two types of networks. (1) {Country-to-theme network} is a bipartite network where connecting two types of nodes, country and theme nodes, and edge weights are computed by aggregating all documents from the same countries. (2) {Country-to-country network} is a unipartite network where nodes are countries, and the weight of an edge between two countries is given by the cosine similarity of the two countries' aggregated theme distributions.

Related Publication:
Tsai, C. H. and Lin, Y.-R. (2014), From Media Reporting to International Relations: A Case Study of Asia-Pacific Economic & Cooperation (APEC). Proceedings of WebScience 2014 (WebSci 2014) 
