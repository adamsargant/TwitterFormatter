import sublime, sublime_plugin, re, math

class TwitterFormatterJumpCommand(sublime_plugin.TextCommand):
    limit = 140
    def run(self, edit):
        allcontent = sublime.Region(0, self.view.size())
        sentences = self.view.substr(allcontent).split('\n')
        toolong = []
        for index in range(len(sentences)):
            if len(sentences[index])>self.limit:
                toolong.append(index)
        pt = self.view.text_point(toolong[0], 0);
        self.view.sel().clear()
        self.view.sel().add(sublime.Region(pt))
        self.view.show(pt, True)

class TwitterFormatterCommand(sublime_plugin.TextCommand):

    limit = 140
    caps = "([A-Z])"
    prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
    suffixes = "(Inc|Ltd|Jr|Sr|Co)"
    starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
    acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
    websites = "[.](com|net|org|io|gov)"

    def run(self, edit):
        allcontent = sublime.Region(0, self.view.size())
        string = self.view.substr(allcontent);
        string = string.replace("’","'")
        string = string.replace("“",'"')
        string = string.replace("”",'"')
        sentences = self.split_into_sentences(string)
        self.displaysentences(edit, sentences)

    def displaysentences(self, edit, sentences):
        allcontent = sublime.Region(0, self.view.size())
        toolong = []
        for index in range(len(sentences)):
            if len(sentences[index])>self.limit:
                toolong.append(index)
        newline = "\n";
        self.view.replace(edit, allcontent, newline.join( sentences ))
        if len(toolong)>0:
            action = sublime.yes_no_cancel_dialog('There are currently ' + str(len(toolong)) + ' lines that are over ' + str(self.limit), 'Best guess split long lines', 'Jump to next large line')
            if action == sublime.DIALOG_YES:
                self.bestguesssplit(edit, sentences)
            if action == sublime.DIALOG_NO:
                pt = self.view.text_point(toolong[0], 0);
                self.view.sel().clear()
                self.view.sel().add(sublime.Region(pt))
                self.view.show(pt, True)

    def bestguesssplit(self, edit, sentences):
        needles = ['" "', '; ', ': ', ', ']
        for nindex in range(len(needles)):
            newsentences = []
            needle = needles[nindex]
            for index in range(len(sentences)):
                if len(sentences[index])>self.limit:
                    pos = math.ceil(sentences[index].count(needle)/2)
                    print(sentences[index].count(needle)/2)
                    print(pos)
                    print(needle)
                    print(sentences[index])
                    if pos>0:
                        position = self.find_nth(sentences[index], needle, pos)
                        newsentences.append(sentences[index][:position+1])
                        newsentences.append(sentences[index][position+2:])
                    else:
                        newsentences.append(sentences[index])
                else:
                    newsentences.append(sentences[index])
            sentences = newsentences
        self.displaysentences(edit, sentences)

    def find_nth(self, haystack, needle, n):
        start = haystack.find(needle)
        while start >= 0 and n > 1:
            start = haystack.find(needle, start+len(needle))
            n -= 1
        return start

    def split_into_sentences(self, text):
        """http://stackoverflow.com/questions/4576077/python-split-text-on-sentences"""
        text = " " + text + "  "
        text = text.replace("\n"," ")
        text = re.sub(self.prefixes,"\\1<prd>",text)
        text = re.sub(self.websites,"<prd>\\1",text)
        if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
        text = re.sub("\s" + self.caps + "[.] "," \\1<prd> ",text)
        text = re.sub(self.acronyms+" "+self.starters,"\\1<stop> \\2",text)
        text = re.sub(self.caps + "[.]" + self.caps + "[.]" + self.caps + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
        text = re.sub(self.caps + "[.]" + self.caps + "[.]","\\1<prd>\\2<prd>",text)
        text = re.sub(" "+self.suffixes+"[.] "+self.starters," \\1<stop> \\2",text)
        text = re.sub(" "+self.suffixes+"[.]"," \\1<prd>",text)
        text = re.sub(" " + self.caps + "[.]"," \\1<prd>",text)
        if "”" in text: text = text.replace(".”","”.")
        if "\"" in text: text = text.replace(".\"","\".")
        text = text.replace(".",".<stop>")
        text = text.replace("<prd>",".")
        sentences = text.split("<stop>")
        sentences = sentences[:-1]
        sentences = [s.strip() for s in sentences]
        return sentences
