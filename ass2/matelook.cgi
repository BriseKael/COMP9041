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

    # is login 0 -> not. 1 -> yes.
    $session_db = "./.cookies";
    %session = %{retrieve($session_db)} if -r $session_db;

    
    # print "user_id=$user_id\n";
    # print "Env: $ENV{QUERY_STRING}\n";
    # print "user_pass=$user_pass\n";

    # In page_header, got the user id from cookie.
    # check user_id in session,
    # if is logined, it will be '1'.
    # otherwise, it will go back to login.cgi
    $is_login = '0';
    $is_login = $session{$user_id} if $session{$user_id};


    if ($is_login eq '0')
    {
        # not login
        # go to matelook to login
        print <<eof;
<meta http-equiv="refresh" content="0; url=./login.cgi">
eof

    }
    elsif ($is_login eq "1")
    {
        # user information
        # display who?
        # if no query string, then display person himself.
        if ($ENV{QUERY_STRING} =~ /user_name=(.*)/)
        {
            $username = $1;
        }
        else
        {
            $username = $user_id;
        }
        
        
        # header div
        print <<eof;
<div class="matelook_header">
    <a href="./matelook.cgi">HOME PAGE</a>
    <div class="matelook_tittle">
        <label class="matelook_tittle_label">Matelook</label>
    </div>
eof
        print log_out();
        print <<eof;
</div>
<div class="matelook_body">
eof
        # main page div

        $user_file = "./$users_dir/$username/user.txt";
        $user_img = "./$users_dir/$username/profile.jpg";

        $user_posts = "./$users_dir/$username/posts";

        # user page print
        $user_inf_p = user_page();

        # recent posts print
        recent_post();

        # mate list print
        mate_list();
        print <<eof;
</div>
eof
    }

    print page_trailer();
}


sub log_out
{
    $is_log_out = param('m') || '1';

    if ($is_log_out eq 'Log_out')
    {
        # session user id turn to '0' to indicate it is log out.

        $session{$user_id} = '0';
        store(\%session, $session_db);

        return <<eof
<meta http-equiv="refresh" content="0; url=./login.cgi">
eof
    }
    else
    {
        return <<eof
    <div class="matelook_logout">
        <form method="POST" action="" class="">
            <button type="submit" name="m" value="Log_out" class="matelook_logout_button">Log_out</button>
        </form>
    </div>
eof
    }
}


# give a zid, return a \hash.
# store one user information
sub find_user_zid
{
    my $zid = $_[0];
    my $this_user_file = "./$users_dir/$zid/user.txt";
    my $this_user_img = "./$users_dir/$zid/profile.jpg";
    my %this_user_inf = ();
    open F, "<$this_user_file";
    while (my $line = <F>)
    {
        if ($line =~ m/zid=(.*)/)
        {
            $this_user_inf{'zid'} = $1;
            chomp($this_user_inf{'zid'});
        }
        if ($line =~ m/full_name=(.*)/)
        {
            $this_user_inf{'full_name'} = $1;
            chomp($this_user_inf{'full_name'});
        }
        if ($line =~ m/program=(.*)/)
        {
            $this_user_inf{'program'} = $1;
            chomp($this_user_inf{'program'});
        }
        if ($line =~ m/home_suburb=(.*)/)
        {
            $this_user_inf{'home_suburb'} = $1;
            chomp($this_user_inf{'home_suburb'});
        }
        if ($line =~ m/birthday=(.*)/)
        {
            $this_user_inf{'birthday'} = $1;
            chomp($this_user_inf{'birthday'});
        }
        if ($line =~ m/mates=(.*)/)
        {
            $this_user_inf{'mates'} = $1;
            chomp($this_user_inf{'mates'});
        }
    }
    close F;
    $this_user_inf{'src'} = $this_user_img if -r $this_user_img;
    return \%this_user_inf;
}

# give a name, return a \array.
# stroe a list of users information
sub find_user_name
{
    my $zname = $_[0];
    my @user_inf_paths = sort(glob("./$users_dir/*"));

    my @these_users_infs = ();

    foreach my $user_inf_path (@user_inf_paths)
    {
        my %this_user_inf = ();
        my $this_user_inf_path = "$user_inf_path/user.txt";
        my $this_user_img = "./$user_inf_path/profile.jpg";
        if (-r $this_user_inf_path)
        {
            open F, "<$this_user_inf_path";
            while (my $line = <F>)
            {
                if ($line =~ m/zid=(.*)/)
                {
                    $this_user_inf{'zid'} = $1;
                    chomp($this_user_inf{'zid'});
                }
                if ($line =~ m/full_name=(.*)/)
                {
                    $this_user_inf{'full_name'} = $1;
                    chomp($this_user_inf{'full_name'});
                }
            }
            close F;
            $this_user_inf{'src'} = $this_user_img if -r $this_user_img;
            if ($this_user_inf{'full_name'} =~ /$zname/ || $this_user_inf{'zid'} =~ /$zname/)
            {
                push @these_users_infs, \%this_user_inf;
            }
        }
    }
    # print "lalala -> @these_users_infs\n";
    return \@these_users_infs;
}

# /
# Show unformatted details for user id.
#
sub user_page 
{
    my %user_inf = %{find_user_zid($username)};

    $details = '<p>';
    foreach my $key (sort keys %user_inf)
    {
        if ($key ne 'src' && $key ne 'mates')
        {
            $details .= "$key: ".$user_inf{$key}.'<p>';
        }
    }

    print <<eof;
    <div class="matelook_body1">
        <h1 class="matelook_body1_h1">$user_inf{'full_name'}</h1>
eof

    if (defined $user_inf{'src'})
    {
        print <<eof;
        <img class="matelook_body_image" src="$user_inf{'src'}">
eof
    }

    print <<eof;
        $details
    </div>
eof
    return \%user_inf;
}

# give a zid, return a hash{time}{zid} = message;

sub find_post
{
    # "./$users_dir/$username/posts";
    my $zid = $_[0];
    my @user_posts_path = sort(glob("./$users_dir/$zid/posts/*"));

    # posts is a hash list for posts.
    my %posts;

    my $this_post_number = 0;
    foreach my $post_to_show (@user_posts_path)
    {
        my $post_to_show_path = "$post_to_show/post.txt";
        # print "$post_to_show_path\n";
        if (-r $post_to_show_path)
        {
            open F, "<$post_to_show_path";

            # this_post is a hash list for post message, have keys: from, time, message.
            my %this_post;
            while (my $line = <F>)
            {
                if ($line =~ m/from=(.*)/)
                {
                    $this_post{'from'} = $1;
                    chomp($this_post{'from'});
                    
                }
                if ($line =~ m/time=(.*)/)
                {
                    $this_post{'time'} = $1;
                    chomp($this_post{'time'});
                    # print "$send_time\n";
                }
                if ($line =~ m/message=(.*)/)
                {
                    $this_post{'message'} = $1;
                    chomp($this_post{'message'});
                    # print "$send_message\n";
                }
            }
            $posts{$this_post_number} = \%this_post;
            close F;
        }
        $this_post_number++;
    }
    return \%posts;
}

sub recent_post
{
    # "./$users_dir/$username/posts";
    print <<eof;
<div class="matelook_body2">
    <div class="matelook_search">
        <form method="POST" name="Find_post_form" action="" class="">
            <input type="textfield" name="post_name" autofocus placeholder="Please enter the key word">
            <button type="submit" name="post_name_button" class="matelook_button">Search</button>
        </form>
    </div>
    <div class="">
eof
    my %self_posts = %{find_post($username)};
    my @self_posts_numbers = sort keys %self_posts;
    foreach my $self_posts_number (sort keys %self_posts)
    {
        # print "$self_posts_number\n";
        my $post_id = @self_posts_numbers - 1 - $self_posts_number;
        my %this_post = %{$self_posts{$post_id}};
        my $this_message = $this_post{'message'};
        $this_message =~ s/\\n/<p>/g;

        my %post_user_inf = %{find_user_zid($this_post{'from'})};
        # $this_post{'from'} is the user zid.
        # $post_id is the post id.
        # path should be: ./$users_dir/$this_post{'from'}/posts/$post_id/comments
        # comments/comments_id/comment.txt

        print <<eof;
        <div class="matelook_post">
            <a href="./matelook.cgi?user_name=$this_post{'from'}">$post_user_inf{'full_name'}</a><p>$this_post{'time'}</p>
            <p>$this_message</p>
eof
        ## handle the comment.
        my $comment_path = "./$users_dir/$this_post{'from'}/posts/$post_id/comments";
        if (-r $comment_path)
        {
            my @comments_paths = reverse(sort(glob("$comment_path/*")));

            my $this_comment_number = @comments_paths - 1;
            foreach my $this_comment_path (@comments_paths)
            {
                my $this_comment_file = "$this_comment_path/comment.txt";

                if (-r $this_comment_file)
                {
                    open F, "<$this_comment_file";

                    my %this_comment;
                    while (my $line = <F>) 
                    {  
                        
                        if ($line =~ m/from=(.*)/)
                        {
                            $this_comment{'from'} = $1;
                            chomp($this_comment{'from'});
                            
                        }
                        if ($line =~ m/time=(.*)/)
                        {
                            $this_comment{'time'} = $1;
                            chomp($this_comment{'time'});
                            # print "$send_time\n";
                        }
                        if ($line =~ m/message=(.*)/)
                        {
                            $this_comment{'message'} = $1;
                            chomp($this_comment{'message'});
                            # print "$send_message\n";
                        }
                    }
                    close F;
                    my %comment_user_inf = %{find_user_zid($this_comment{'from'})};
                    my $this_comment_message = $this_comment{'message'};
                    $this_comment_message =~ s/\\n/<p>/g;
                    print <<eof;
            <div class="matelook_post">
                <a href="./matelook.cgi?user_name=$this_comment{'from'}">$comment_user_inf{'full_name'}</a><p>$this_comment{'time'}</p>
                <p>$this_comment_message</p>
            </div>        
eof
                }
                $this_comment_number--;
            }
        }

        print <<eof;
        </div>
eof
    }

    print <<eof
    </div>
</div>
eof
}




sub mate_list
{
    print <<eof;
<div class="matelook_body3">
    <div class="matelook_find_mate">
        <form method="POST" name="Find_mate_form" action="" class="">
            <input type="textfield" name="finder_name" autofocus placeholder="Mate name">
            <button type="submit" name="finder_name_button" class="matelook_button">Search</button>
        </form>
    
eof
    my $finder_name = param('finder_name') || '';
    # my $finder_name_button = param('finder_name_button') || '';

    if ($finder_name ne '')
    {
        print <<eof;
        <h3>Search Results for \'$finder_name\'</h3>
    </div>
eof
        # do search
        my @results = @{find_user_name($finder_name)};
        foreach $result (@results)
        {
            # print "$result\n";
            print <<eof;
    <div class="matelook_mate_list">
        <div class="matelook_mate_list">
eof
            %this_user = %{$result};
            # print "$this_user{'src'}\n";
            if (defined $this_user{'src'})
            {
                print <<eof;
    
            <a href="./matelook.cgi?user_name=$this_user{'zid'}"><img class="main_page_body_image" src="$this_user{'src'}"></a>
            <p>
eof
            }
            print <<eof;
            <a href="./matelook.cgi?user_name=$this_user{'zid'}">$this_user{'zid'}</a>
            <p>
            <p>$this_user{'full_name'}</p>
            <p>
        </div>
    </div>
eof
        }
    }
    else
    {
        print <<eof;
        <h3>Mate List</h3>
    </div>
    <div class="matelook_mate_list">
eof

        my @mates_list = split(', ', %{$user_inf_p}->{'mates'});
        foreach my $mate (@mates_list)
        {
            print <<eof;
            <div class="matelook_mate_list">
eof
            $mate =~ s/[\[\] ]//g;
            my %mate_inf = %{find_user_zid($mate)};

            if (defined $mate_inf{'src'})
            {
                print <<eof;
                <a href="./matelook.cgi?user_name=$mate_inf{'zid'}"><img class="main_page_body_image" src="$mate_inf{'src'}"></a>
                <p>
eof
            }
            print <<eof;
                <a href="./matelook.cgi?user_name=$mate_inf{'zid'}">$mate_inf{'zid'}</a>
                <p>
                <p>$mate_inf{'full_name'}</p>
                <p>
            </div>
eof
        }
        print <<eof;
        </div>
eof
    }
    print <<eof;
</div>
eof
    # 

}




#
# HTML placed at the top of every page
# 
sub page_header
{
    $user_id = 0;
    # $user_pass = 0;
    
    if ($ENV{HTTP_COOKIE} =~ /\buser_id=([^;]+)/)
    {
        $user_id = $1;
    }

    # there must be an empty line before !DOCYPE html.
    return <<eof
Content-Type: text/html;charset=utf-8
Set-Cookie: user_id=$user_id;

<!DOCTYPE html>
<html lang="en">
<head>
<title>Matelook. What's happening</title>
<link href="matelook.css" rel="stylesheet">
</head>
<body>

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