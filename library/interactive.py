import requests
import re

SRT_SAMPLE = """1
00:00:00,000 --> 00:00:04,044
One, thank you for taking the time to
listen to this pre-recorded session.

2
00:00:04,044 --> 00:00:06,049
This session is called No Dough for
Donuts and

3
00:00:06,049 --> 00:00:08,328
it's about food insecurity
on college campuses.

4
00:00:08,328 --> 00:00:12,434
And you will also learn about
some different initiatives

5
00:00:12,434 --> 00:00:15,340
that you can do on your college campus and

6
00:00:15,340 --> 00:00:19,891
hopefully help students that
identify with food insecurity.

7
00:00:19,891 --> 00:00:22,527
Before we kind of get started just
a little bit of an introduction.

8
00:00:22,527 --> 00:00:26,219
My name is Anna Brown,
my preferred pronouns are she, her, hers.

9
00:00:26,219 --> 00:00:29,222
I work at William Peace University
in housing and

10
00:00:29,222 --> 00:00:31,722
residence life as an Area Coordinator.

11
00:00:31,722 --> 00:00:34,160
A couple other things about
me is I love to travel.

12
00:00:34,160 --> 00:00:37,454
While I travel I would love to
explore different coffee shops and

13
00:00:37,454 --> 00:00:39,652
I also love exploring different gardens.

14
00:00:39,652 --> 00:00:44,565
And if I can get the opportunity to I
love taking flower arranging classes and

15
00:00:44,565 --> 00:00:46,652
just being able to be in nature.

16
00:00:46,652 --> 00:00:50,537
A couple things that I really hope
everyone is able to take away from today

17
00:00:50,537 --> 00:00:54,170
is have a better understanding about
what food insecurity means and

18
00:00:54,170 --> 00:00:56,033
how it affects college students.

19
00:00:56,033 --> 00:00:59,800
I also really hope that everyone is able
to take away some small initiatives and

20
00:00:59,800 --> 00:01:03,854
some larger initiatives that you can
incorporate into your day-to-day role, but

21
00:01:03,854 --> 00:01:07,051
also bring back to your institution
to hopefully have it on a larger

22
00:01:07,051 --> 00:01:07,817
scale as well.

23
00:01:07,817 --> 00:01:09,327
What is food insecurity?

24
00:01:09,327 --> 00:01:11,405
Food insecurity does not
mean that you're hungry.

25
00:01:11,405 --> 00:01:13,831
It means where is my
next meal coming from.

26
00:01:13,831 --> 00:01:19,442
And so to put into a bit of a perspective
is so a student has to kind of map out and

27
00:01:19,442 --> 00:01:23,154
think about where their
next meal is coming from.

28
00:01:23,154 --> 00:01:25,478
For example, Monday morning at 7:00 AM,

29
00:01:25,478 --> 00:01:29,122
that student knows that they can go
to the dining hall and get breakfast.

30
00:01:29,122 --> 00:01:31,810
Or a student can go to
a late night program and

31
00:01:31,810 --> 00:01:33,928
get a couple pieces of pizza to go.

32
00:01:33,928 --> 00:01:37,499
And it really is a student mapping
out where they can get food,

33
00:01:37,499 --> 00:01:42,102
how they can get food, and hoping that
they don't have to spend as much money and

34
00:01:42,102 --> 00:01:43,286
having to dine out.

35
00:01:43,286 --> 00:01:47,117
And also not having a lot of
groceries around as well too.

36
00:01:47,117 --> 00:01:50,822
So really, the student thinking and
trying to map out a game plan for

37
00:01:50,822 --> 00:01:53,886
how they will get their
nutrition throughout the week.

38
00:01:53,886 --> 00:01:58,913
Some statistics that I'd like to share
with you and a fact in some vulnerable

39
00:01:58,913 --> 00:02:03,801
populations is 29% of college
students fit the traditional profile.

40
00:02:03,801 --> 00:02:07,921
And the traditional profile
is the student's parent is,

41
00:02:07,921 --> 00:02:11,208
the student's family is paying for
college.

42
00:02:11,208 --> 00:02:14,355
The parents are able to
support their student, and

43
00:02:14,355 --> 00:02:16,339
the student does not have a job.

44
00:02:16,339 --> 00:02:19,777
There's also means the student can
call their parents and say, hey,

45
00:02:19,777 --> 00:02:22,528
can you put $100 in my account and
then parents can.

46
00:02:22,528 --> 00:02:28,113
71% of students might have family support,
but they also are needing to have a job or

47
00:02:28,113 --> 00:02:31,723
take out significant loans to
be able to pay for school.

48
00:02:31,723 --> 00:02:36,866
Down below you'll see the 2018
survey results from the Hope Center.

49
00:02:36,866 --> 00:02:41,858
The Hope Center is an organization
from Philadelphia out of Philadelphia,

50
00:02:41,858 --> 00:02:46,928
PA and it kind of does the breakdown of
food insecurity, housing insecure and

51
00:02:46,928 --> 00:02:52,237
then homeless population at two-year
colleges and four-year institutions.

52
00:02:52,237 --> 00:02:56,728
Some vulnerable populations that
really have identified with food

53
00:02:56,728 --> 00:02:59,412
insecurity is students with children.

54
00:02:59,412 --> 00:03:03,677
Being a parent is already a lot to juggle,
but then you add in school that you're

55
00:03:03,677 --> 00:03:07,899
trying to finish that degree and then
also trying to feed yourself and a child.

56
00:03:07,899 --> 00:03:11,197
There's a lot going on there in a lot
that as somebody has to balance.

57
00:03:11,197 --> 00:03:16,914
Pell Grant Recipients, returning citizens,
older students, foster youth,

58
00:03:16,914 --> 00:03:21,634
LGBTQ plus, a couple with foster care,
an LGBTQ plus community.

59
00:03:21,634 --> 00:03:25,315
Sometimes a student might
have family support, but

60
00:03:25,315 --> 00:03:27,909
then they go home for spring break and

61
00:03:27,909 --> 00:03:33,279
decide that they tell their parents
that they identify in this population.

62
00:03:33,279 --> 00:03:36,156
And the parents might
not agree with that and

63
00:03:36,156 --> 00:03:39,200
then they cut off their
student financially.

64
00:03:39,200 --> 00:03:43,710
Foster youth, a student might have gone
through the foster care system and

65
00:03:43,710 --> 00:03:46,430
are then not able to have
the support system or

66
00:03:46,430 --> 00:03:50,740
have the finances that are available
to them that other students have.

67
00:03:50,740 --> 00:03:54,364
Impact on students missing,
late or failed courses,

68
00:03:54,364 --> 00:03:58,554
sleep deprivation, unpaid tuition,
inadequate supplies.

69
00:03:58,554 --> 00:04:01,955
Students might not have the money for
all their textbooks.

70
00:04:01,955 --> 00:04:06,479
Students might not also have the funds
to purchase graphing calculators or

71
00:04:06,479 --> 00:04:11,452
science equipment, and so they are not
able to be as successful in the classroom.

72
00:04:11,452 --> 00:04:13,798
Lack of involvement on campus.

73
00:04:13,798 --> 00:04:17,511
They might not be able to be involved
on campus and be a part of a campus

74
00:04:17,511 --> 00:04:22,209
activities board or a student government
association or just a student organization

75
00:04:22,209 --> 00:04:26,406
in general because they are already
trying to balance work and school work.

76
00:04:26,406 --> 00:04:29,715
And just, getting in some sleep.

77
00:04:29,715 --> 00:04:32,188
And then also adding in
homework as well too.

78
00:04:32,188 --> 00:04:34,928
They are always students
that are having to juggle so

79
00:04:34,928 --> 00:04:37,169
much aren't always able to enjoy sports or

80
00:04:37,169 --> 00:04:41,104
be involved with areas that they know
that they're passionate about too.

81
00:04:41,104 --> 00:04:45,388
This also takes a big toll on their
emotional and mental well-being.

82
00:04:45,388 --> 00:04:50,497
Being so strung out and being pulled in so
many different directions

83
00:04:50,497 --> 00:04:55,693
can harm a student a lot mentally and
then not getting enough sleep and

84
00:04:55,693 --> 00:05:01,445
not getting enough nutrition really
impacts them on a day-to-day basis.

85
00:05:01,445 --> 00:05:06,317
Food for thought just to be mindful
when your meeting with students

86
00:05:06,317 --> 00:05:08,666
is who's in the students life?

87
00:05:08,666 --> 00:05:11,116
Does this student have a support network?

88
00:05:11,116 --> 00:05:16,108
Has the student gone through
the foster care system?

89
00:05:16,108 --> 00:05:20,880
Why is this student maybe not
getting involved on campus?

90
00:05:20,880 --> 00:05:24,514
Are there any other underlying
reasons why a student might be

91
00:05:24,514 --> 00:05:26,232
struggling academically.

92
00:05:26,232 --> 00:05:29,683
And so just kind of thinking about these
things when you're getting to know

93
00:05:29,683 --> 00:05:30,231
students or

94
00:05:30,231 --> 00:05:33,860
working with previous students too is
really starting to build that rapport.

95
00:05:33,860 --> 00:05:37,143
So that then they do feel
comfortable saying to you, hey,

96
00:05:37,143 --> 00:05:40,164
I have a lot of different jobs and
I'm juggling a lot.

97
00:05:40,164 --> 00:05:43,485
I really wish I could be involved,
but I really don't.

98
00:05:43,485 --> 00:05:45,893
I really don't have the time
because I am going to work and

99
00:05:45,893 --> 00:05:47,409
doing a bunch of different things.

100
00:05:47,409 --> 00:05:49,757
And so building that rapport with them so

101
00:05:49,757 --> 00:05:53,910
then they do feel that they can trust
you and give you this information.

102
00:05:53,910 --> 00:05:58,284
And from that then you being able to
provide them with great resources and

103
00:05:58,284 --> 00:06:01,016
being able to support
the student even more.

104
00:06:01,016 --> 00:06:02,804
How can you help?

105
00:06:02,804 --> 00:06:06,874
These are just some small things that you
can do in your day-to-day work in your

106
00:06:06,874 --> 00:06:08,098
offices and stuff too.

107
00:06:08,098 --> 00:06:11,674
First off,
just knowing your institution's resources,

108
00:06:11,674 --> 00:06:16,759
knowing the community's resources,
you can start a take-what-you-need box.

109
00:06:16,759 --> 00:06:20,136
Having this in your office suite or
having this within lobby halls,

110
00:06:20,136 --> 00:06:23,945
in residence halls and stuff and just
putting a couple cans of soup in there.

111
00:06:23,945 --> 00:06:28,180
And people can put items in there,
somebody can walk by and

112
00:06:28,180 --> 00:06:32,760
take a can of soup, but
it's a very anonymous way that a student

113
00:06:32,760 --> 00:06:36,577
can get an extra meal or
get some extra supplies too.

114
00:06:36,577 --> 00:06:40,944
When you're doing tabling events you
do health packets or study bags or

115
00:06:40,944 --> 00:06:44,145
study packets and stuff,
and that's an easy way for

116
00:06:44,145 --> 00:06:48,384
a student to be able to take something and
say, This is awesome.

117
00:06:48,384 --> 00:06:49,557
Finals are coming up.

118
00:06:49,557 --> 00:06:50,362
This is great and

119
00:06:50,362 --> 00:06:54,224
then they can save themselves some money
on buying a package of index cards too.

120
00:06:54,224 --> 00:06:58,032
And it's a very anonymous way that then
a student doesn't necessarily have

121
00:06:58,032 --> 00:07:00,424
to come out and open up and
say I'm struggling.

122
00:07:00,424 --> 00:07:01,504
I need help.

123
00:07:01,504 --> 00:07:06,390
Another way too is having a bulletin
board with different resources on it too

124
00:07:06,390 --> 00:07:08,539
that students can go by and grab.

125
00:07:08,539 --> 00:07:09,921
You could do tear off sheets.

126
00:07:09,921 --> 00:07:13,207
Whatever fits you the best in your style.

127
00:07:13,207 --> 00:07:17,378
And then also maybe doing a snack
basket in your office, granola bars,

128
00:07:17,378 --> 00:07:18,501
things like that.

129
00:07:18,501 --> 00:07:20,791
That is student can grab
on their way out too and

130
00:07:20,791 --> 00:07:23,330
give someone an extra little
snack in their hands.

131
00:07:23,330 --> 00:07:28,896
So institution initiatives, one of them
is a campus food pantry and there's a lot

132
00:07:28,896 --> 00:07:34,303
of logistics and a lot of moving parts
with starting any of these initiatives and

133
00:07:34,303 --> 00:07:38,904
I'm happy to talk with anybody that
would like to get that started,

134
00:07:38,904 --> 00:07:41,187
share any documents that I have.

135
00:07:41,187 --> 00:07:45,761
And kind of share the do's and
don'ts and kind of what I've learned

136
00:07:45,761 --> 00:07:50,428
from working with two different
food pantries on college campuses.

137
00:07:50,428 --> 00:07:54,186
The swipe it forward program and
collaboration with your dining hall,

138
00:07:54,186 --> 00:07:57,766
last I knew this was an 86 different
institutions across campus.

139
00:07:57,766 --> 00:08:01,423
Also a way to get other students involved.

140
00:08:01,423 --> 00:08:03,571
Also getting alumni involved too.

141
00:08:03,571 --> 00:08:08,694
Having a resource hub, so having a central
area on your institution's website

142
00:08:08,694 --> 00:08:14,275
where all of the financial resources,
counseling resources, tutoring resources,

143
00:08:14,275 --> 00:08:18,652
any resource that's free for
a college student is all in one place.

144
00:08:18,652 --> 00:08:22,854
And students can go and like look through
and see who they need to contact and

145
00:08:22,854 --> 00:08:25,003
what that offices offers as well too.

146
00:08:25,003 --> 00:08:29,464
Having a food insecurity statement in
their syllabuses is this is something I've

147
00:08:29,464 --> 00:08:31,339
seen colleges start to do as well,

148
00:08:31,339 --> 00:08:34,070
especially in their first
year seminar classes.

149
00:08:34,070 --> 00:08:38,656
But also expanding into all of their class
syllabuses that faculty put together and

150
00:08:38,656 --> 00:08:41,343
it's just a statement
about food insecurity and

151
00:08:41,343 --> 00:08:44,960
the resources that are on campus
that are available to students.

152
00:08:44,960 --> 00:08:47,607
Another great way is
getting alumni involved.

153
00:08:47,607 --> 00:08:52,194
Asking alumni to do a food drive, adding
alumni to purchase a block of meals or for

154
00:08:52,194 --> 00:08:57,069
Swipe It Forward, or purchasing grocery
gift cards anything along those lines too.

155
00:08:57,069 --> 00:09:00,494
And alumni love being engaged and
love giving back to an institution.

156
00:09:00,494 --> 00:09:05,038
The last thing is there are tons of
different grants out there that you can

157
00:09:05,038 --> 00:09:09,134
apply for for your institution too
that I know off the top of my head

158
00:09:09,134 --> 00:09:11,768
is Harris Teeter and the Chobani yogurt.

159
00:09:11,768 --> 00:09:15,409
They have grants that you can fill out and
they will give you funding for

160
00:09:15,409 --> 00:09:18,501
a food pantry to get started or
just any funding in general.

161
00:09:18,501 --> 00:09:23,263
I do know a lot of this is going to look
a little bit different this fall with

162
00:09:23,263 --> 00:09:27,950
COVID-19 and all of us navigating that,
but I definitely think that

163
00:09:27,950 --> 00:09:33,130
everyone can with brainstorming and
just kind of figuring out those details.

164
00:09:33,130 --> 00:09:38,911
Resources in Raleigh you will get
a handout with all of these resources,

165
00:09:38,911 --> 00:09:44,624
the address of the location and
the phone number, hours of operation.

166
00:09:44,624 --> 00:09:48,419
And I will make sure everyone gets
that after the presentation is over,

167
00:09:48,419 --> 00:09:52,402
but these are just a few in Raleigh, A
Place at the Table is one that I have had

168
00:09:52,402 --> 00:09:55,015
experience volunteering at,
fabulous place.

169
00:09:55,015 --> 00:09:56,827
It's a pay what you can cafe and

170
00:09:56,827 --> 00:10:01,783
it's a great place to bring students that
are very passionate about volunteering,

171
00:10:01,783 --> 00:10:06,454
but it's also a great place that students
can go and pay what they can for a meal or

172
00:10:06,454 --> 00:10:10,398
go and get a free meal because
they're just waiting on a paycheck.

173
00:10:10,398 --> 00:10:13,802
Or they can go and have a free meal and
then will still work for an hour and

174
00:10:13,802 --> 00:10:15,495
kind of get back to the community.

175
00:10:15,495 --> 00:10:19,350
But that is a great organization
in downtown Raleigh and

176
00:10:19,350 --> 00:10:23,541
all these other organizations
have been fantastic as well.

177
00:10:23,541 --> 00:10:28,443
Resources slash helpful reads, the Hope
Center out of Philadelphia, PA fantastic

178
00:10:28,443 --> 00:10:32,654
resource, great speakers, great folks
doing great work about this and

179
00:10:32,654 --> 00:10:36,106
trying to help their institutions
with food insecurity and

180
00:10:36,106 --> 00:10:38,750
helping students across the United States.

181
00:10:38,750 --> 00:10:43,707
The Carolina College Hunger Summit.

182
00:10:43,707 --> 00:10:46,969
There was a conference that I got to go
through last year and it was fantastic.

183
00:10:46,969 --> 00:10:51,372
I learned a lot, got to network with lots
of other different folks that work at

184
00:10:51,372 --> 00:10:53,001
different institutions and

185
00:10:53,001 --> 00:10:57,639
have put together food truck put together
grants all kinds of different things.

186
00:10:57,639 --> 00:10:59,381
So it was a great conference to go to.

187
00:10:59,381 --> 00:11:02,166
And that was run by
Second Harvest Food Bank,

188
00:11:02,166 --> 00:11:06,785
I do not know if they have put out
information for this year's conference,

189
00:11:06,785 --> 00:11:09,888
but it's definitely
something to keep an eye on.

190
00:11:09,888 --> 00:11:11,443
And if I do hear anything,

191
00:11:11,443 --> 00:11:14,857
I can try to get that information
out to everyone as well.

192
00:11:14,857 --> 00:11:18,781
A great read is Homeless and Hungry
at America's Most Beautiful College.

193
00:11:18,781 --> 00:11:20,093
The College of Charleston.

194
00:11:20,093 --> 00:11:23,664
It's a great read just to
kind of get more of an idea,

195
00:11:23,664 --> 00:11:27,244
especially on a college
that's very close by to us.

196
00:11:27,244 --> 00:11:30,205
Chicken Soup for
the Soul Volunteering and Giving.

197
00:11:30,205 --> 00:11:34,686
And then lastly, I would just
get managed by Carrie Morgridge.

198
00:11:34,686 --> 00:11:37,959
All these were great resources and
stuff too, and there's also so

199
00:11:37,959 --> 00:11:40,956
much more out there that I hope
people can take advantage of.

200
00:11:40,956 --> 00:11:45,661
I really appreciate you guys taking the
time to listen to this presentation and

201
00:11:45,661 --> 00:11:49,865
I hope that you join in for the upcoming
discussion that we will have and

202
00:11:49,865 --> 00:11:53,657
please bring any questions and
I will do my best to answer them.

203
00:11:53,657 --> 00:11:58,713
Slash direct you in the right place and
also provide any helpful documents or

204
00:11:58,713 --> 00:12:01,250
any helpful pieces about logistics.

205
00:12:01,250 --> 00:12:03,776
Or if you are interested in
starting a food pantry or

206
00:12:03,776 --> 00:12:06,730
starting any of these initiatives
on your college campus.

207
00:12:06,730 --> 00:12:09,586
Thank you so much and have a great day.

208
00:12:09,586 --> 00:12:12,850
[NO_SPEECH]"""

def duration_to_sec(val):
  # Simple function to convert HH:MM:SS,MMM or HH:MM:SS.MMM to SS.MMM
  # Assume valid, returns 0 on error
  return val

class HyperLine(object):
  def __init__(self, index, content):
    self.index = index
    self.content = content
    self.line_type = "new_line"
    if self.index and self.content:
      self.set_line_type()

  def set_line_type(self):
    line_type = self.identify_line_type()
    self.line_type = line_type
    return line_type

  def identify_line_type(self):
    try:
      formatted_line = self.content.strip().replace("\n", "")

      # Perform timecode check
      if "-->" in formatted_line:
        return "timecode"

      # Perform index check
      raw_index = int(formatted_line)
      if raw_index in range(0, 999999):
        return "index"

      # Perform content check
      else:
        return "content"
    except Exception as e:
      return "content"

class HyperAudio(object):
  def __init__(self, lines=None):
    self.lines = lines
    self.hyperlines = []
    self.blocks = []
    self.header = '<article><header></header><section><header></header><p>'
    self.footer = '</p><footer></footer></section></footer></footer></article>'
    self.text = ''
    self.split_mode = False
    self.new_content_element = '<a data-m="{0}">{1}</a>'
    self.word_length_split = False
    self.para_split_timing = 1000
    self.hyperelement = ""
    self._blocks = {}

  def to_json(self):
    print(self.__dict__)
    return self.__dict__
  
  def generate_hyper_elements(self):
    self.hyperelement += self.header
    for block in self._blocks.items():
      block[1].construct_hyper_words()
      block[1].construct_hyper_element()
      self.hyperelement += block[1].hyperblock
      self.hyperelement += "</br></br>"
    self.hyperelement += self.footer
    return self.hyperelement

  def add_block(self, block, overwrite=False):
    idx = block["index"]
    print(idx, block)
    self._blocks[idx] = block
    self.blocks = self._blocks
    return self.blocks

  def parse_hyperlines(self):
    hyperlines = []
    num_lines = len(self.lines)
    count = 0
    for line in self.lines:
      count += 1
      line_obj = HyperLine(count, line)
      hyperlines.append(line_obj)
    self.hyperlines = hyperlines
    return self.hyperlines

  def add_block(self, block):
    block_key = block.index
    self._blocks[block_key] = block
    return self.blocks

  def construct_blocks(self):
    assert self.hyperlines
    # Start at Line One
    count = 1
    current_block = Block(index=count)
    for line in self.hyperlines:
      if line.line_type == "new_line":
        if current_block.is_complete():
          count += 1
          self.add_block(current_block)
          current_block = new_block(count)
          continue
      if line.line_type == "index":
        current_block.add_index_line(line)
      if line.line_type == "timecode":
        current_block.add_timecode_line(line)
      if line.line_type == "content":
        current_block.add_content_line(line)


  def print_block_repr(self):
    assert self._blocks
    for index, block in self._blocks.items():
      print(block)
    return

  def print_hyperlines(self):
    for line in self.hyperlines:
      print("Index: {0} | Type: {1} | Content: {2}".format(line.index, line.line_type, line.content))

def new_block(index):
  return Block(index)

class Block(object):
  def __init__(self, index):
    self.index = index
    self.timecode = None
    self.index_line = None
    self.content_lines = []
    self.hyperlines = []
    self.hyperwords = []
    self.hyper_element = []
    self.line_start = 0
    self.line_end = 0
    self.current_line = 0
    self.parent_line = 0
    self.hyperblock = ""
    self.start_time = 0
    self.end_time = 0
    self.new_content_element = '<a data-m="{0}"> {1}</a>'

  def is_complete(self):
    has_index = self.index_line if self.index_line else False
    has_timecode = self.timecode if self.timecode else False
    has_content = True if len(self.content_lines) > 1 else False
    if has_index and has_timecode and has_content:
      return True
    return False

  def to_string(self):
    output_str = ""
    output_str += self.index_line.content
    output_str += "\n"
    output_str += self.timecode.content
    output_str += "\n"
    for line in self.content_lines:
      output_str += line.content
      output_str += "\n"
    return output_str

  def add_index_line(self, line):
    self.index_line = line
    return self.index_line

  def add_timecode_line(self, line):
    self.timecode = line
    return self.timecode

  def add_content_line(self, line):
    self.content_lines.append(line)
    return self.content_lines

  def set_index(self, index):
    self.index = index
    return self.index

  def set_start_time(self, start_time):
    self.start_time = start_time
    return self.start_time

  def set_end_time(self, end_time):
    self.end_time = end_time
    return self.end_time

  def construct_hyper_element(self):
    for word in self.hyperwords:
      new_line = self.new_content_element.format(word.timestamp, word.content)
      self.hyperblock += new_line
    return self.hyperblock

  def get_start_end_times(self):
    timeline = self.timecode.content.split(" --> ")
    start_time = self.time_to_sec(timeline[0])
    end_time = self.time_to_sec(timeline[1])
    self.start_time = start_time
    self.end_time = end_time
    return start_time, end_time

  def time_to_sec(self, time_str):
    from datetime import datetime
    ts = datetime.strptime(time_str, "%H:%M:%S,%f")
    a_timedelta = ts - datetime(1900, 1, 1)
    seconds = a_timedelta.total_seconds()
    return seconds

  def set_start_time(self, start_time):
    assert self.timecode
    self.start_time = start_time
    return self.start_time

  def set_end_time(self, end_time):
    assert self.timecode
    self.end_time = end_time
    return self.end_time

  def get_duration(self):
    diff = float(self.end_time) - float(self.start_time)
    return diff

  def construct_hyper_words(self):
    self.get_start_end_times()
    letters_in_word = 0
    count = 1
    for line in self.content_lines:
      line_duration = self.get_duration()
      per_word_duration = line_duration / len(line.content.split(" "))
      for word in line.content.split(" "):
        timestamp = self.start_time + (per_word_duration * count)
        timestamp *= 1000
        timestamp = round(timestamp)
        hyperword = HyperWord(block_id=self.index, word_index=count, timestamp=timestamp, content=word)
        self.hyperwords.append(hyperword)
        count += 1

    def print_hyperwords(self):
      print(self.hyperwords)

  def escape_and_format_content(self, text):
    formatted_text = text.replace()
    return formatted_text

class HyperWord(object):
  def __init__(self, block_id, word_index, timestamp, content):
    self.block_id = block_id
    self.word_index = word_index
    self.timestamp = timestamp
    self.content = content

# def convert_srt_to_hyperaudio():
#   lines = SRT_SAMPLE.split("\n")
#   ht = HyperAudio(lines=lines)
#   ht.parse_hyperlines()
#   # ht.print_hyperlines()
#   ht.construct_blocks()
#   print(ht.__dict__)
#   ht_html_string = ht.generate_hyper_elements()
#   f = open('ht.html', 'w+')
#   f.write(ht_html_string)
#   f.close()

def convert_srt_to_hyperaudio(content):
  lines = content.split("\n")
  ht = HyperAudio(lines=lines)
  print(ht.__dict__)
  ht.parse_hyperlines()
  # ht.print_hyperlines()
  ht.construct_blocks()
  ht_html_string = ht.generate_hyper_elements()
  return ht_html_string