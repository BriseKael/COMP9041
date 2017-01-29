#!/usr/bin/perl -w


use CGI qw/:all/;

use CGI::Carp qw/fatalsToBrowser warningsToBrowser/;

use Storable;

sub main() 
{
    # print start of HTML ASAP to assist debugging if there is an error in the script
    print page_header();
    
    # Now tell CGI::Carp to embed any warning in HTML
    warningsToBrowser(1);
    
    # define some global variables
    $debug = 1;
    $users_dir = "dataset-medium"; 

    # session for server to record the user
    $session_db = "./.cookies";
    %session = %{retrieve($session_db)} if -r $session_db;

    # print the login page.
    login_page();

    # tailer
    print page_trailer();
}

sub login_page
{
    $username = param("username") || '';
    $password = param("password") || '';
    $pwd = '';

    if ($username && $password)
    {
        my $user_file = "./$users_dir/$username/user.txt";
        if (open F, "<$user_file")
        {
            while (my $line = <F>)
            {
                if ($line =~ m/password=(.*)/)
                {
                    $pwd = $1;
                    chomp($pwd);
                    last;
                }
            }
            close F;
            if ($password eq $pwd)
            {
                print "$username authenticated.\n";

                # username and the password are both correct.
                # store the userid in session and set it to '1' which indicate it is logined.
                $user_id = $username;
                $session{$user_id} = '1';
                store(\%session, $session_db);
                print <<eof;
<meta http-equiv="refresh" content="0; url=./matelook.cgi">
eof
                return;
            }
            else
            {
                # print "password is wrong.\n";
                print <<eof;
<form method="POST" name="Login_in_form" action="" class="login_input">
    <input type="textfield" name="username" autofocus placeholder="Username or zID" class="login_input_text">
    <p>
    <input type="password" name="password" autofocus placeholder="Password" class="login_input_text">
    <p>
    <p>Password is wrong</p>
    <p>
    <button type="submit" class="login_button">Login</button>
</form>
eof
                return;
            }
        }
        else
        {
            # print "User name is wrong.\n";
            print <<eof;
<form method="POST" name="Login_in_form" action="" class="login_input">
    <input type="textfield" name="username" autofocus placeholder="Username or zID" class="login_input_text">
    <p>
    <p>User name is wrong</p>
    <p>
    <input type="password" name="password" autofocus placeholder="Password" class="login_input_text">
    <p>
    <button type="submit" class="login_button">Login</button>
</form>
eof
            return;
        }
    }
    elsif (!$username && $password)
    {
        # print "require username\n";
        print <<eof;
<form method="POST" name="Login_in_form" action="" class="login_input">
    <input type="textfield" name="username" autofocus placeholder="Username or zID" class="login_input_text">
    <p>
    <p>Require UserName</p>
    <p>
    <input type="password" name="password" autofocus placeholder="Password" class="login_input_text">
    <p>
    <button type="submit" class="login_button">Login</button>
</form>
eof
        return;
    }
    elsif ($username && !$password)
    {
        # print "require password\n";
        print <<eof;
<form method="POST" name="Login_in_form" action="" class="login_input">
    <input type="textfield" name="username" autofocus placeholder="Username or zID" class="login_input_text">
    <p>
    <input type="password" name="password" autofocus placeholder="Password" class="login_input_text">
    <p>
    <p>Require password</p>
    <p>
    <button type="submit" class="login_button">Login</button>
</form>
eof
        return;
    }
    print <<eof
<form method="POST" name="Login_in_form" action="" class="login_input">
    <input type="textfield" name="username" autofocus placeholder="Username or zID" class="login_input_text">
    <p>
    <input type="password" name="password" autofocus placeholder="Password" class="login_input_text">
    <p>
    <button type="submit" class="login_button">Login</button>
</form>
eof
}

#
# HTML placed at the top of every page
# 
sub page_header
{
    

    $user_id = 0;
    # $user_pass = 0;

    if (param('username'))
    {
        $user_id = param('username');
    }
    elsif ($ENV{HTTP_COOKIE} =~ /\buser_id=([^;]+)/)
    {
        $user_id = $1;
    }

    # $user_pass = param('password') || 0;
    
    # if ($ENV{HTTP_COOKIE} =~ /\buser_id=(\d+)/)
    # {
    #     $user_id = $1;
    # }
    
    # there must be an empty line before !DOCYPE html.
    return <<eof
Content-Type: text/html;charset=utf-8
Set-Cookie: user_id=$user_id;

<!DOCTYPE html>
<html lang="en">
<head>
<title>Matelook. What's happening</title>
<link href="login.css" rel="stylesheet">
</head>
<body>
<div class="login_header">
    <label class="">Matelook</label>
</div>
eof
}





#
# HTML placed at the bottom of every page
# It includes all supplied parameter values as a HTML comment
# if global variable $debug is set
#

sub page_trailer 
{
    my $html = "";
    $html .= join("", map("<!-- $_=".param($_)." -->\n", param())) if $debug;
    $html .= end_html;
    return $html;
}

main();
