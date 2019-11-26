"""
    Student No: 180008512
"""

from nltk.corpus import brown
from nltk import FreqDist, WittenBellProbDist


class HiddenMarkovModel():
    def __init__(self, tagset):
        self.taggedSents = brown.tagged_sents(tagset=tagset)
        self.startTag = "<s>"
        self.endTag = "</s>"
        self.trainSents, self.testSents = self.splitSents(self.taggedSents)
        self.words, self.tags, self.uTags = self.splitWordsAndTags()
        self.tagsProbDis, self.wordsProbDis = self.probabilityDis()

        kParam = 1
        option = 1
        while option != 0:
            print("\n *** MAIN MENU *** \n Please choose an option: \n  1. Run Algorithm 1 (Viterbi) \n  2. Run Algorithm 2 (Eager algorithm and beam search) \n  0. Exit \n")
            option = input("  Option: ")
            if option == "1":
                self.algorithm1()
            elif option == "2":
                option2 = ""
                print("\n  K parameter is set to 1 by default, would you like to define a new K parameter? ")
                option2 = input("\n  y/Y for yes, n/N for no: ")
                if option2 == "y" or option2 == "Y":
                    kParam = input("\n  New K param: ")
                    self.algorithm2(int(kParam))
                else:
                    self.algorithm2(kParam)
            else:
                print("\n Exiting program...")
                option = 0

    def splitSents(self, sents):
        training = []
        testing = []
        for i in range(10500):
            sent = sents[i]
            sent.insert(0, (self.startTag, self.startTag))
            sent.append((self.endTag, self.endTag))
            if i < 10000:
                training.append(sent)
            else:
                testing.append(sent)
        return training, testing

    def splitWordsAndTags(self):
        words = []
        tags = []
        for sent in self.trainSents:
            words += [w for (w, _) in sent]
            tags += [t for (_, t) in sent]
        uTagsSet = set(tags)
        uTagsList = list(uTagsSet)
        return words, tags, uTagsList

    def probabilityDis(self):
        tagsDis = {}
        wordsDis = {}
        for tag in self.uTags:
            tags = []
            words = []
            for i in range(len(self.tags)):
                if tag == self.tags[i]:
                    words.append(self.words[i])
                    if i < (len(self.tags) - 1):
                        tags.append(self.tags[i + 1])
            tagsDis[tag] = WittenBellProbDist(FreqDist(tags), bins=1e5)
            wordsDis[tag] = WittenBellProbDist(FreqDist(words), bins=1e5)
        return tagsDis, wordsDis

    def algorithm2(self, k):
        finalSents = []
        testCase = 1
        total = 0
        count = 0
        for sent in self.testSents:
            sent = self.testSents[0]
            finalSent = []
            bestSequence = []
            trelli = []
            endPoint = []
            for q in range(len(sent)-1):
                trelli.append([])
            for i in range(len(sent)):
                word = sent[i]
                if word[0] == "<s>":
                    continue
                elif i == 1:
                    for j in range(k):
                        highest = 0
                        t = ""
                        for tag in self.uTags:
                            transition = self.tagsProbDis["<s>"].prob(tag)
                            emission = self.wordsProbDis[tag].prob(word[0])
                            viterbi = transition * emission
                            if j == 0:
                                if viterbi > highest:
                                    highest = viterbi
                                    t = tag
                            else:
                                check = "f"
                                for q in range(j):
                                    if trelli[1][q][2] == tag:
                                        check = "t"
                                if check != "t":
                                    if viterbi > highest:
                                        highest = viterbi
                                        t = tag
                        trelli[1].append((highest, "<s>", t))
                elif word[0] == "</s>":
                    best = 0
                    prev = ""
                    for j in range(k):
                        transition = self.tagsProbDis[trelli[i - 1][j][2]].prob("</s>")
                        viterbi = trelli[i - 1][j][0]
                        viterbi = viterbi * transition
                        if viterbi > best:
                            best = viterbi
                            prev = trelli[i - 1][j][2]
                    endPoint.append((best, prev, "</s>"))
                else:
                    for j in range(k):
                        best = 0
                        prev = ""
                        t = ""
                        for tag in self.uTags:
                            emission = self.wordsProbDis[tag].prob(word[0])
                            transition = self.tagsProbDis[trelli[i - 1][j][2]].prob(tag)
                            viterbi = trelli[i-1][j][0]
                            viterbi = viterbi * transition * emission
                            if viterbi > best:
                                best = viterbi
                                prev = trelli[i-1][j][2]
                                t = tag
                        trelli[i].append((best, prev, t))

            prevTag = endPoint[0][1]
            bestSequence.append("</s>")
            for i in range(len(trelli)-1, 0, -1):
                bestSequence.insert(0, prevTag)
                for j in range(k):
                    if prevTag == trelli[i][j][2]:
                        prevTag = trelli[i][j][1]

            bestSequence.insert(0, "<s>")

            for i in range(len(sent)):
                word = sent[i]
                finalSent.append((word[0], bestSequence[i]))

            finalSents.append(finalSent)
            print("\n Test: ", testCase, " ----------------------------", "\n EXPECTED OUTPUT \n")
            print(sent, "\n\n ********** \n ACTUAL OUTPUT \n")
            print(finalSent)
            testCase += 1

            for w in range(len(finalSent)):
                total += 1
                if finalSent[w] == sent[w]:
                    count += 1

        accuracy = (1.0*count/total)*100
        print("\n Accuracy: ", accuracy, "%")
        return finalSents

    def algorithm1(self):
        finalSents = []
        testCase = 1
        total = 0
        count = 0
        for sent in self.testSents:
            sent = self.testSents[0]
            finalSent = []
            bestSequence = []
            trelli = []
            endPoint = []
            for q in range(len(sent)-1):
                trelli.append([])
            for i in range(len(sent)):
                word = sent[i]
                if word[0] == "<s>":
                    continue
                elif i == 1:
                    for tag in self.uTags:
                        transition = self.tagsProbDis["<s>"].prob(tag)
                        emission = self.wordsProbDis[tag].prob(word[0])
                        viterbi = transition * emission
                        trelli[i].append((viterbi, "<s>"))
                elif word[0] == "</s>":
                    best = 0
                    prev = ""
                    for tag in self.uTags:
                        transition = self.tagsProbDis[tag].prob("</s>")
                        index = self.uTags.index(tag)
                        viterbi = trelli[i-1][index][0]
                        viterbi = viterbi * transition
                        if viterbi > best:
                            best = viterbi
                            prev = tag
                    endPoint.append((best, prev))
                else:
                    for tag in self.uTags:
                        best = 0
                        prev = ""
                        emission = self.wordsProbDis[tag].prob(word[0])
                        for t in self.uTags:
                            transition = self.tagsProbDis[t].prob(tag)
                            index = self.uTags.index(t)
                            viterbi = trelli[i-1][index][0]
                            viterbi = viterbi * transition * emission
                            if viterbi > best:
                                best = viterbi
                                prev = t
                        trelli[i].append((best, prev))

            prevTag = endPoint[0][1]
            bestSequence.append("</s>")
            for i in range(len(trelli)-1, 0, -1):
                bestSequence.insert(0, prevTag)
                prevTag = trelli[i][self.uTags.index(prevTag)][1]

            bestSequence.insert(0, "<s>")

            for i in range(len(sent)):
                word = sent[i]
                finalSent.append((word[0], bestSequence[i]))

            finalSents.append(finalSent)
            print("\n Test: ", testCase, " ----------------------------", "\n EXPECTED OUTPUT \n")
            print(sent, "\n\n ********** \n ACTUAL OUTPUT \n")
            print(finalSent)
            testCase += 1

            for w in range(len(finalSent)):
                total += 1
                if finalSent[w] == sent[w]:
                    count += 1

        accuracy = (1.0*count/total)*100
        print("\n Accuracy: ", accuracy, "%")
        return finalSents


def main():
    tagset = "universal"
    hmm = HiddenMarkovModel(tagset)


if __name__ == '__main__':
    main()























