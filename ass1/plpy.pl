#!/usr/bin/perl -w

sub usrbin
{
    if ($_[0] =~ /^#!/ && $. == 1) 
    {
        # translate #! line 
        $_[0] = "#!/usr/local/bin/python3.5 -u";
        push @head, "#!/usr/local/bin/python3.5 -u";
    } 
    return $_[0];
}

sub keyword
{
    if ($_[0] =~ /^(.*)(\d)\.\.(\d)(.*)$/)
    {
        $endnumber = $3 + 1;
        $_[0] = "$1range($2, $endnumber)$4";
    }

    if ($_[0] =~ /^(.*)join\(\s*(.*),\s*(\@\w+)\)(.*)$/)
    {
        $_[0] = "$1$2.join($3)$4";
    }
    if ($_[0] =~ /^(.*)split\(\s*[\/\"\'](.*)[\/\"\'],\s*(\$\w+)\)(.*)$/)
    {
        $_[0] = "$1$3.split(\'$2\')$4";
    }


    if ($_[0] =~ /^(.*)\@ARGV(.*)$/)
    {
        $find = 0;
        foreach $line (@head)
        {
            if ($line eq "import sys")
            {
                $find = 1;
            }
        }
        if ($find == 0)
        {
            push @head, "import sys";
        }
        $_[0] = "$1sys.argv[1:]$2";
    }
    
    return $_[0];
}

sub linecomment
{
    if ($line =~ /^\s*#/ || $line =~ /^\s*$/) 
    {
        # Blank & comment lines can be passed unchanged
    }
    return $_[0];
}

sub lineif
{
    # this is a line with if
    if ($_[0] =~ /^(\s*)}?\s*if\s*\((.*)\)\s*{?$/)
    {
        $word  =$2;
        $word = wordphase($word);
        $word = wordlogic($word);
        $_[0] = "$1if $word:";
    }
    elsif ($_[0] =~ /^(\s*)}?\s*elsif\s*\((.*)\)\s*{?$/)
    {
        $word  =$2;
        $word = wordphase($word);
        $word = wordlogic($word);
        $_[0] = "$1elif $word:";
    }
    elsif ($_[0] =~ /^(\s*)}?\s*else\s*{?$/)
    {
        $_[0] = "$1else:";
    }
    return $_[0];
}

sub linewhile
{
    if ($_[0] =~ /^(\s*)while\s*\(\s*(\$\w+)\s*\=\s*\<STDIN\>\s*\)\s*{?$/)
    {
        $find = 0;
        foreach $line (@head)
        {
            if ($line eq "import sys")
            {
                $find = 1;
            }
        }
        if ($find == 0)
        {
            push @head, "import sys";
        }
        $_[0] = "$1for $2 in sys.stdin:";
    }
    # this is a line with while
    if ($_[0] =~ /^(\s*)while\s*\((.*)\)\s*{?$/)
    {
        $word  =$2;
        $word = wordphase($word);
        $word = wordlogic($word);
        $_[0] = "$1while $word:";
    }

    return $_[0];
}

sub lineforeach
{
    # this is a line with while
    if ($_[0] =~ /^(\s*)foreach\s*(\$\w+)\s*\((.*)\)\s*{?$/)
    {
        $_[0] = "$1for $2 in $3:";
    }

    return $_[0];
}

sub linefor
{
    if ($_[0] =~ /^(\s*)for\s*\((.*)\)\s*{?$/)
    {
        
        $spaces = $1;
        @condition = split(/;/, $2);
        if ($condition[0] =~ /^\s*(\$\w+)\s*\=\s*(\d+)\s*$/)
        {
            $var = $1;
            $startnum = $2;
        }
        if ($condition[1] =~ /^\s*(\$\w+)\s*[\<|\>]\s*(\d+)\s*$/)
        {
            $var = $1;
            $endnum = $2;
        }
        if ($condition[2] =~ /^\s*(\$\w+)\s*\+\+\s*$/)
        {
            if ($condition[1] =~ /^\s*(\$\w+)\s*\<\=\s*(\d+)\s*$/)
            {
                $var = $1;
                $endnum = $2+1;
            }
            $_[0] = "${spaces}for ${var} in range(${startnum}, ${endnum}):";
        }
        if ($condition[2] =~ /^\s*(\$\w+)\s*\-\-\s*$/)
        {
            if ($condition[1] =~ /^\s*(\$\w+)\s*\>\=\s*(\d+)\s*$/)
            {
                $var = $1;
                $endnum = $2-1;
            }
            $_[0] = "${spaces}for ${var} in range(${startnum}, ${endnum}, -1):";
        }

    }
    return $_[0];
}

sub lineprint
{
    if ($_[0] =~ /^.*\".*\\n\"[\s;]*$/)
    {
        if ($_[0] =~ /^(\s*)print\s*"([\$\@].*)\\n"[\s;]*$/)
        {
            $_[0] = "$1print($2)";
        }
        elsif ($_[0] =~ /^(\s*)print\s*"(.*)\\n"[\s;]*$/) 
        {
            $_[0] = "$1print(\"$2\")";
        }
        elsif ($_[0] =~ /^(\s*)print\s*(.*)$/)
        {
            $spaces = $1;
            @values = split(/,/, $2);
            if ($values[$#values] =~ /\s*\"\\n\"/)
            {
               pop(@values);
            }
            $_[0] = "${spaces}print(@values)";
        }
    }
    else
    {
        if ($_[0] =~ /^(\s*)print\s*"([\$\@].*)"[\s;]*$/)
        {
            $_[0] = "$1print($2, end = \"\")";
        }
        elsif ($_[0] =~ /^(\s*)print\s*"(.*)"[\s;]*$/) 
        {
            $_[0] = "$1print(\"$2\", end = \"\")";
        }
    }
    
    return $_[0];
}

sub linevariable
{
    if ($_[0] =~ /^(\s*)(\$\w+)\s*\=\s*(.*)[\s;]*$/)
    {
        # $line = <STDIN>; -> line = sys.stdin.readline()
        # push import sys
        $word = $3;
        $word = wordphase($word);
        $_[0] = "$1$2 = $word"
    }
    return $_[0];
}

sub lineelse
{
    if ($_[0] =~ /^(\s*)next[\s;]*$/)
    {
        $_[0] = "$1continue";
    }
    if ($_[0] =~ /^(\s*)last[\s;]*$/)
    {
        $_[0] = "$1break";
    }
    if ($_[0] =~ /^(\s*)chomp\s*(\$\w+)[\s;]*$/)
    {
        $_[0] = "$1$2 = $2.rstrip()";
    }

    if ($_[0] =~ /^(\s*)(\$\w+)\s*\+\+[\s;]*$/)
    {
        $_[0] = "$1$2 += 1";
    }
    if ($_[0] =~ /^(\s*)(\$\w+)\s*\-\-[\s;]*$/)
    {
        $_[0] = "$1$2 -= 1";
    }
    
    return $_[0];
}



sub wordphase
{
    if ($_[0] =~ /^\s*\<STDIN\>[\s;]*$/)
    {
        $find = 0;
        foreach $line (@head)
        {
            if ($line eq "import sys")
            {
                $find = 1;
            }
        }
        if ($find == 0)
        {
            push @head, "import sys";
        }
        $_[0] = "sys.stdin.readline()"
    }
    
    return $_[0];
}

sub wordlogic
{
    if ($_[0] =~ /^\s*(.*)\s*\|\|\s*(.*)[\s;]*$/)
    {
        $_[0] = "$1 or $2";
    }
    elsif ($_[0] =~ /^\s*(.*)\s*\&\&\s*(.*)[\s;]*$/)
    {
        $_[0] = "$1 and $2";
    }

    if ($_[0] =~ /^\s*([\$\"\']\w+[\"\']?)\s*lts*([\$\"\']\w+[\"\']?)[\s;]*$/)
    {
        $_[0] = "$1 < $2";
    }
    elsif ($_[0] =~ /^\s*([\$\"\']\w+[\"\']?)\s*gt\s*([\$\"\']\w+[\"\']?)[\s;]*$/)
    {
        $_[0] = "$1 > $2";
    }
    elsif ($_[0] =~ /^\s*([\$\"\']\w+[\"\']?)\s*le\s*([\$\"\']\w+[\"\']?)[\s;]*$/)
    {
        $_[0] = "$1 <= $2";
    }
    elsif ($_[0] =~ /^\s*([\$\"\']\w+[\"\']?)\s*ge\s*([\$\"\']\w+[\"\']?)[\s;]*$/)
    {
        $_[0] = "$1 >= $2";
    }
    elsif ($_[0] =~ /^\s*([\$\"\']\w+[\"\']?)\s*eq\s*([\$\"\']\w+[\"\']?)[\s;]*$/)
    {
        $_[0] = "$1 == $2";
    }
    elsif ($_[0] =~ /^\s*([\$\"\']\w+[\"\']?)\s*ne\s*([\$\"\']\w+[\"\']?)[\s;]*$/)
    {
        $_[0] = "$1 != $2";
    }
    return $_[0];
}


@head = ();
# store the usrbin and import line.

while ($line = <>) 
{
    chomp($line);

    # usr/bin/perl -> usr/local/bin/python3.5
    $line = usrbin($line);

    $line = keyword($line);

    $line = linecomment($line);
    $line = lineif($line);
    $line = linewhile($line);
    $line = lineforeach($line);
    $line = linefor($line);
    $line = lineprint($line);
    $line = linevariable($line);
    $line = lineelse($line);

    if ($line =~ /\$\w+/)
    {
        # replace the '$'
        # may have errors...
        $line =~ s/\$//g;
    }
    if ($line =~ /\@\w+/)
    {
        # replace the '$'
        # may have errors...
        $line =~ s/\@//g;
    }
    if ($line =~ /^.+;$/)
    {
        # replace the ';'
        ($line) = $line =~ /^(.+);$/;
    }

    if ($line =~ /^\s*[{|}]\s*$/)
    {
        # print "";
        # push @lines, $line;
        next;
    }
    elsif ($line eq "#!/usr/local/bin/python3.5 -u")
    {
        next;
    }
    else
    {
        # print "$line\n";
        push @lines, $line;
    }
}

foreach $line (@head)
{
    print "$line\n";
}

foreach $line (@lines)
{
    print "$line\n";
}
