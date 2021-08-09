import re

import scrapy

from tpc_crawler.items import *


class InfocomTpcSpider(scrapy.Spider):
    name = 'infocom_tpc_spider'

    start_urls = [
        # New INFOCOM (using p selector)
        'https://infocom2021.ieee-infocom.org/committees/tpc-members',
        'https://infocom2020.ieee-infocom.org/committee/tpc-members',
        'https://infocom2019.ieee-infocom.org/committee/tpc-members',
        'https://infocom2018.ieee-infocom.org/committee/tpc-members',
        # New INFOCOM (using div selector)
        'https://infocom2017.ieee-infocom.org/committee/tpc-members',
        'https://infocom2016.ieee-infocom.org/committee/tpc-members',
        'https://infocom2015.ieee-infocom.org/committee/tpc-members',
        # Infocom 13-14
        'https://infocom2014.ieee-infocom.org/Committees_TPC.html',
        'https://infocom2013.ieee-infocom.org/tpcmembers.html',
        # Old Infocom with tables
        'https://infocom2012.ieee-infocom.org/TPCmembers.html',
        'https://infocom2011.ieee-infocom.org/TPCmembers.html',
        'https://infocom2010.ieee-infocom.org/TPC_Chairs.html',
        # Infocom with table layout
        'https://infocom2008.ieee-infocom.org/TPC_Chairs.html',
        'https://infocom2007.ieee-infocom.org/tpc.html',
        'https://infocom2006.ieee-infocom.org/programcommi.htm',
        'https://infocom2005.ieee-infocom.org/tpc_members.htm',
        'https://web.archive.org/web/20151028105305/https://infocom2004.ieee-infocom.org/TPC.htm',
        'https://infocom2003.ieee-infocom.org/tpc_members.htm',
        # INFOCOM 2009 - extracted from https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=5061895 as
        # it's no longer accessible from the original website
        'https://infocom2009.ieee-infocom.org/',
    ]

    def parse(self, response, **kwargs):
        # Get the year of conference from url
        year_expr = re.compile(r'infocom(\d+)')
        conf_year = int(year_expr.findall(response.url)[0])

        if conf_year >= 2015:
            tpc = self.parse_new(response, conf_year)
        elif conf_year == 2014 or conf_year == 2013:
            tpc = self.parse_2014(response, conf_year)
        elif conf_year >= 2010:
            tpc = self.parse_old(response, conf_year)
        elif conf_year == 2009:
            tpc = self.get_2009()
        else:
            tpc = self.parse_legacy(response, conf_year)

        yield TpcItem(ConferenceType.INFOCOM, conf_year, tpc)

    def parse_new(self, response, year):
        # Get the tpc list (the last three entries are explanations to the "medal"
        # in authors' names which we don't want)
        if year == 2019:
            tpc = response.css('div.field-items p::text').getall()[:-2]
        elif year >= 2018:
            tpc = response.css('div.field-items p::text').getall()[:-3]
        else:
            tpc = response.css('div.field-items div::text').getall()[:-1]
        # Remove the affiliation information, note that some names contains a weird "\u200b" character which needs
        # to be removed
        tpc = [name.split('(')[0].strip().replace('\u200b', '') for name in tpc]
        # Remove the empty strings resulting from newline characters
        tpc = [member for member in tpc if member and ')' not in member]
        return tpc

    def parse_2014(self, response, year):
        # Get the list of TPC members
        if year == 2014:
            tpc = response.css('div#content::text').getall()
        else:
            tpc = response.css('div#page p::text').getall()
        # Remove the affiliation information
        tpc = [name.split(',')[0] for name in tpc]
        tpc = [re.sub(r' \(.*\)', '', name).strip() for name in tpc]
        # Remove the empty strings resulting from newline characters
        tpc = [member for member in tpc if member]

        return tpc

    def parse_old(self, response, year):
        if year == 2012 or year == 2010:
            if year == 2012:
                # Get the names (broken into first and last names)
                tpc_first = response.xpath('//table[@class="committee"]//tr/td[1]/text()').getall()
                # Get the last name
                tpc_last = response.xpath('//table[@class="committee"]//tr/td[2]/text()').getall()
            else:
                tpc_first = response.xpath('//table[@id="table2"]//tr/td[1]/font/text()').getall()
                tpc_last = response.xpath('//table[@id="table2"]//tr/td[2]/font/text()').getall()
            # Some first names contain nicknames - clean them
            tpc_first = [name.split('(')[0].strip() for name in tpc_first]
            tpc = [' '.join(name) for name in zip(tpc_first, tpc_last)]
        else:
            tpc = response.xpath('//table[@class="committee"]//tr/td[1]/text()').getall()[1:]
            # Remove the nickname and extra whitespace from the name
            tpc = [re.sub(r' \(.*\)', '', name).strip() for name in tpc]
        return tpc

    def parse_legacy(self, response, year):
        # Obtain the list of TPC members
        if year == 2008:
            tpc = response.xpath('//table//table//table//table//tr/td[1]/text()').getall()
            # Remove extra whitespace and nickname in parentheses in the name
            tpc = [' '.join(re.sub(r' \(.*\)', '', name).replace('\n', '').split()) for name in tpc]
        elif year == 2007:
            tpc = response.xpath('//table[@class="MsoNormalTable"]//tr/td[1]//text()').getall()
        elif year == 2006:
            tpc = response.xpath('//tr/td[1]//text()').getall()
        elif year == 2005 or year == 2003:
            tpc = response.css('td.xl24 ::text').getall()
        elif year == 2004:
            tpc = response.xpath('//table//table//tr/td[1]/text()').getall()[2:]
        else:
            # Shouldn't happen
            tpc = []
        # Remove the empty strings resulting from newline characters
        # Remove the extra \r\n in the name
        tpc = [' '.join(name.split()) for name in tpc]
        tpc = [member.strip() for member in tpc]
        tpc = [member for member in tpc if member]

        return tpc

    def get_2009(self):
        return ['Alhussein Abouzeid', 'Sharad Agarwal', 'Dakshi Agrawal', 'Aditya Akella', 'Ehab Al-Shaer',
                'Jussara Almeida', 'Kevin Almeroth', 'Sara Alouf', 'Tansu Alpcan', 'Eitan Altman', 'Matthew Andrews',
                'Arturo Azcorra', 'Francois Baccelli', 'Sujata Banerjee', 'Suman Banerjee', 'Chadi Barakat',
                'Prithwish Basu', 'Brahim Bensaou', 'Azer Bestavros', 'Samrat Bhattacharjee', 'Saleem Bhatti',
                'Giuseppe Bianchi', 'Andrea Bianco', 'Olivier Bonaventure', 'Anat Bremler-Barr', 'Timothy Brown',
                'Tian Bu', 'Milind Buddhikot', 'Levente Buttyan', 'John Byers', 'Lin Cai', 'Hector Cancela',
                'Guohong Cao', 'Srdjan Capkun', 'Antonio Capone', 'Claudio Casetti', 'Meeyoung Cha',
                'Augustin Chaintreau', 'Surendar Chandra', 'H. Jonathan Chao', 'Mainak Chatterjee', 'Yan Chen',
                'Songqing Chen', 'Yingying Chen', 'Shigang Chen', 'Yu Cheng', 'Xiuzhen Cheng', 'Jay Cheng',
                'Liang Cheng', 'Mung Chiang', 'A. Chockalingam', 'Chen-Nee Chuah', 'Mooi Choo Chuah', 'Song Ci',
                'Marco Conti', 'Yi Cui', 'Jun-Hong Cui', 'Francesca Cuomo', 'John Daigle', 'Samir Das', 'Sajal Das',
                'Luiz A. DaSilva', 'Jaudelice de Oliveira', 'Piet Demeester', 'Michael Devetsikiotis',
                'Christophe Diot', 'Jordi Domingo-Pascual', 'Yingfei Dong', 'Olivier Dousse', 'Constantine Dovrolis',
                'Falko Dressler', 'Xiaojiang Du', 'Zhenhai Duan', 'Otto Duarte', 'Rudra Dutta', 'Alon Efrat',
                'Lars Eggert', 'Eylem Ekici', 'Tamer ElBatt', 'Mohamed Eltoweissy', 'Ozgur Ercetin', 'Atilla Eryilmaz',
                'Do Young Eun', 'Sonia Fahmy', 'Faramarz Fekri', 'Anja Feldmann', 'Wu-chang Feng', 'Wu-chun Feng',
                'Timur Friedman', 'Xiaoming Fu', 'Xinwen Fu', 'Richard Gail', 'Deepak Ganesan', 'Michele Garetto',
                'Majid Ghaderi', 'Christos Gkantsidis', 'Dennis Goeckel', 'Nada Golmie', 'Sergey Gorinsky',
                'Manimaran Govindarasu', 'Marco Gruteser', 'Yong Guan', 'Chuanxiong Guo', 'Minaxi Gupta',
                'Piyush Gupta', 'Omer Gurewitz', 'Ting He', 'Tian He', 'Nidhi Hegde', 'Wendi Heinzelman', 'Ahmed Helmy',
                'Y. Charlie Hu', 'Yih-Chun Hu', 'Jianwei Huang', 'Aravind Iyer', 'Manish Jain', 'Hani Jamjoom',
                'Predrag Jelenkovic', 'Chuanyi Ji', 'Xiaohua Jia', 'Zhen Jiang', 'Tao Jiang', 'Ramesh Johari',
                'Changhee Joo', 'Jason Jue', 'Ahmed Kamal', 'Koushik Kar', 'Thomas Karagiannis', 'Sneha Kasera',
                'Anne-Marie Kermarrec', 'Isaac Keslassy', 'Ramin Khalili', 'Arzad Kherani', 'Edward Knightly',
                'Bong Jun Ko', 'M. Kodialam', 'Can Emre Koksal', 'Ramana Rao Kompella', 'Sastry Kompella',
                'Farinaz Koushanfar', 'Iordanis Koutsopoulos', 'Bhaskar Krishnamachari', 'Marwan Krunz',
                'Santosh Kumar', 'Sailesh Kumar', 'Amit Kumar', 'Richard La', 'Tom La Porta', 'Koen Langendoen',
                'Nikolaos Laoutaris', 'Wing Cheong Lau', 'Loukas Lazos', 'Sung-Ju Lee', 'Kang-Won Lee', 'Wonjun Lee',
                'Emilio Leonardi', 'Kin Leung', 'Xiaolin Li', 'Baochun Li', 'Li Li', 'Qun Li',
                'Xiang-Yang Li', 'Jie Li', 'Guangzhi Li', 'Minglu Li', 'Ben Liang', 'Wanjiun Liao', 'Lavy Libman',
                'Xiaojun Lin', 'Christoph Lindemann', 'Bin Liu', 'Peng Liu', 'Alex Liu', 'Yunhao Liu', 'Mingyan Liu',
                'Yonghe Liu', 'Xin Liu', 'Yong Liu', 'Xue Liu', 'Benyuan Liu', 'Jiangchuan Liu', 'Renato Lo Cigno',
                'Francesco Lo Presti', 'Boon Thau Loo', 'Wenjing Lou', 'Wei Lou', 'Steven Low', 'Chenyang Lu',
                'Songwu Lu', 'John Chi Shing Lui', 'Qingming Ma', 'Sridhar Machiraju', 'Allen MacKenzie',
                'Rahul Mangharam', 'Z. Morley Mao', 'Shiwen Mao', 'Madhav Marathe', 'Peter Marbach', 'Brian Mark',
                'Jose Marzo', 'Daniel Massey', 'Laurent Mathy', 'Ravi Mazumdar', 'Marco Mellia', 'Xiaoqiao Meng',
                'Michela Meo', 'Vivek Mhatre', 'Daniele Miorandi', 'Vishal Misra', 'Archan Misra', 'Jeonghoon Mo',
                'Prasant Mohapatra', 'Refik Molva', 'Petar Momcilovic', 'Andrew Moore', 'Thomas Moscibroda',
                'Thyaga Nandagopal', 'Giovanni Neglia', 'Srihari Nelakuditi', 'Hung Ngo', 'Jason Nieh', 'Peng Ning',
                'Cristina Nita-Rotaru', 'Guevara Noubir', 'Pavan Nuggehalli', 'Joerg Ott', 'Fernando Paganini',
                'Sergio Palazzo', 'Jianping Pan', 'Shivendra Panwar', 'Panagiotis Papadimitratos',
                'Vasileios Pappas', 'Kihong Park', 'Jung-Min Park', 'Chiara Petrioli', 'Dhananjay Phatak',
                'Radha Poovendran', 'Alexandre Proutiere', 'Konstantinos Psounis', 'Wangdong Qi', 'Yi Qian',
                'Daji Qiao', 'Lili Qiu', 'Byrav Ramamurthy', 'Bhaskaran Raman', 'Srinivasan Ramasubramanian',
                'Ramachandran Ramjee', 'Sampath Rangarajan', 'Nageswara Rao', 'Sanjay Rao', 'Narasimha Reddy',
                'Reza Rejaie', 'Kui Ren', 'Injong Rhee', 'Rudolf Riedi', 'James Roberts', 'George Rouskas',
                'Rajarshi Roy', 'Romit Roy Choudhury', 'Dan Rubenstein', 'Gerardo Rubino', 'Ashutosh Sabharwal',
                'Hamid Sadjadpour', 'Theodoros Salonidis', 'Iraj Saniee', 'Saswati Sarkar', 'Anna Scaglione',
                'Henning Schulzrinne', 'Subhabrata Sen', 'Sudipta Sengupta', 'Pablo Serrano', 'Mukund Seshadri',
                'Sanjeev Setia', 'Devavrat Shah', 'Aman Shaikh', 'Anees Shaikh', 'Srinivas Shakkottai', 'Sherman Shen',
                'Yi Shi', 'Biplab Sikdar', 'Suresh Singh', 'Prasun Sinha', 'Raghupathy Sivakumar', 'Krishna Sivalingam',
                'Arun Somani', 'Min Song', 'Alex Sprintson', 'Mark Squillante', 'Vikram Srinivasan',
                'Aravind Srinivasan', 'Kotikalapudi Sriram', 'David Starobinski', 'Ioannis Stavrakakis',
                'Martha Steenstrup', 'Dimitrios Stiliadis', 'Aaron Striegel', 'Suresh Subramaniam', 'Yan Sun',
                'Ravi Sundaram', 'Ananthram Swami', 'Violet Syrotiuk', 'Kevin Tang', 'Shu Tao', 'Renata Teixeira',
                'Andreas Terzis', 'Marina Thottan', 'Joe Touch', 'Wade Trappe', 'Ming-Jer Tsai', 'Yu-Chee Tseng',
                'Piet Van Mieghem', 'Athanasios Vasilakos', 'Darryl Veitch', 'Arun Venkataramani', 'Giorgio Ventre',
                'Harish Viswanathan', 'Milan Vojnovic', 'Anil Vullikanti', 'Mehmet Vuran', 'Anwar Walid',
                'Jean Walrand', 'Peng-Jun Wan', 'Yu Wang', 'Ju Wang', 'Haining Wang', 'Chonggang Wang', 'Xinbing Wang',
                'Bin Wang', 'Wenye Wang', 'Xudong Wang', 'Xin Wang', 'Jia Wang', 'Lan Wang', 'Bing Wang',
                'Steven Weber', 'Cedric Westpha', 'Joerg Widmer', 'Carey Williamson', 'Lars Wolf', 'Tilman Wolf',
                'Vincent Wong', 'Thomas Woo', 'Shyhtsun Felix Wu', 'Hongyi Wu', 'Min-You Wu', 'Dapeng Oliver Wu',
                'Ye Xia', 'Cathy Xia', 'Yang Xiao', 'Linda Jiang Xie', 'Chunsheng Xin', 'Shugong Xu', 'Lisong Xu',
                'Dahai Xu', 'Dong Xuan', 'Yuan Xue', 'Yaling Yang', 'Y. Richard Yang', 'Yuanyuan Yang', 'Xue Yang',
                'Hao Yang', 'Mark Yarvis', 'David Yau', 'Fan Ye', 'Edmund Yeh', 'Bulent Yener', 'Lei Ying',
                'Moustafa Youssef', 'Fang Yu', 'Murat Yuksel', 'Murtaza Zafer', 'Hui Zang', 'Daniel Zappala',
                'Petros Zerfos', 'Beichuan Zhang', 'Xiaodong Zhang', 'Honggang Zhang', 'Ying Zhang', 'Yongguang Zhang',
                'Yanchao Zhang', 'Wensheng Zhang', 'Yin Zhang', 'Lisa Zhang', 'Zhi-Li Zhang', 'Junshan Zhang',
                'Xi Zhang', 'Ben Zhao', 'Si-Qing Zheng', 'Rong Zheng', 'Haitao Zheng', 'Gang Zhou', 'Yanmin Zhu',
                'Michael Zink', 'Artur Ziviani', 'Michele Zorzi', 'Moshe Zukerman', 'Gil Zussman']
