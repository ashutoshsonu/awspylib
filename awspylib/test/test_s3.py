#!/usr/bin/env python
# Copyright (c) <2008> <Kiran Bhageshpur - kiran_bhageshpur at hotmail dot com>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

import sys
import os
import os.path
import time
import string


from awspylib.aws_exception import *
from awspylib.aws_config import Config
import awspylib.aws_genutilities as Util
import awspylib.aws_s3.s3_util as S3Util


TEST_FILE_NAME = 'testfile.txt'
TEST_DIR_ROOT = 'TEST-DATA'
NUMBER_OF_DIR_LEVELS = 2
NUMBER_OF_DIR        = 2
NUMBER_OF_FILES      = 3

        
def _create_dir_level_( level, top_dir):

    os.chdir( top_dir)
    for i in range(NUMBER_OF_FILES):
        filename = 'file' + str(level) + '-' + str(i)
        Util.make_test_file( filename)

    if (level < NUMBER_OF_DIR_LEVELS):
        for j in range(NUMBER_OF_DIR):
            dirname = 'dir' + str(level) + '-' + str(j)
            os.mkdir(dirname)
            _create_dir_level_(level+1, dirname )
            
    cur_dir = os.getcwd( )
    k = cur_dir.rfind( os.sep )
    cur_dir = cur_dir[:k]
    os.chdir(cur_dir)
    return

               
def create_test_dir( ):
        
    if ( os.path.exists( TEST_DIR_ROOT) == False ):
        os.mkdir(TEST_DIR_ROOT)
        _create_dir_level_(0, TEST_DIR_ROOT)
    return
            
def test_s3():
    
    create_test_dir( )
    
    conn = S3Util.S3.AWSAuthConnection(Config.AWSProperties['AccessKey'], \
                                       Config.AWSProperties['SecretKey'], ( Config.AWSProperties['SecureComm'] == True))

    AllBuckets = S3Util.AWS_S3( AWSConnectionObject  = conn )


    test = 'TEST-1'
    print '%s: Getting List of Buckets' % test
    try:
        AllBuckets.get_list_of_buckets ( )
    except Exception, e:
        print '\t%s: - FAILED! (%s)' % (test, e)
    else:
        print '\t%s: - Success!' % test


    bucket = u'AWSPyLib-testingbucket98765'
    test = 'TEST-2'
    print '%s: Adding bucket=%s' % (test, bucket)
    try:
        AllBuckets.add_bucket(  bucket )
    except Exception, e:
        print '\t%s: - FAILED! (%s)' % (test, e)
    else:
        print '\t%s: - Success!' % test


    test = 'TEST-3'
    print '%s: Deleting bucket=%s' % (test, bucket)
    try:        
        AllBuckets.delete_bucket(bucket)
    except Exception, e:
        print '\t%s: - FAILED! (%s)' % (test, e)
    else:
        print '\t%s: - Success!' % test


    test = 'TEST-4'
    print '%s: Deleting recursively a non-existant bucket. Should Fail!' % test
    try:
        AllBuckets.delete_bucket_recursive( u'doesnotexist')
    except Exception, e:
        print '\t%s: - Success!' % test
    else:
        print '\t%s: - FAILED! (%s)' % (test, e)


    # If it does not exist, make a local 100KB  test file with random data
    if (os.path.exists ( TEST_FILE_NAME ) == False ):
        Util.make_test_file( TEST_FILE_NAME, 1024*100)
        
    test = 'TEST-5'
    print '%s: Deleting bucket with content' % test
    bucket = u'AWSPyLib-testingbucket98765'
    try:
        AllBuckets.add_bucket(  bucket )
        key = S3Util.AWS_Key(conn, bucket, u'testkey.key')
        key.put_object_from_file ( TEST_FILE_NAME)
        AllBuckets.delete_bucket_recursive (  bucket )
    except Exception, e:
        print '\t%s: - FAILED! (%s)' % (test, e)
    else:
        print '\t%s: - Success!' % test

    bucket = u'AWSPyLib-testingbucket12345'
    AllBuckets.add_bucket( bucket )

    keyName = TEST_FILE_NAME
    
    test = 'TEST-6'
    test_key = S3Util.AWS_Key(conn,bucket, key)
    print '%s: Uploading file=%s to key=%s. Should fail with IOError' % (test, 'nonexistingfile.file', keyName)
    try:
        test_key.put_object_from_file( 'nonexistingfile.file' )
    except Exception, e:
        print '\t%s: - Success' % test
    else:
        print '\t%s: - FAILED' % test
        
    test = 'TEST-7'
    test_key = S3Util.AWS_Key(conn,bucket, keyName)    
    print '%s: Uploading %s to key=%s.  Should succeed!' % (test, TEST_FILE_NAME, keyName)
    try:
        test_key.put_object_from_file( TEST_FILE_NAME )
    except Exception, e:
        print '\t%s: - FAILED! (%s)' % (test, e)
    else:
        print '\t%s: - Success!' % test


    test = 'TEST-8'
    print '%s: Sync Upload %s to key=%s.  Should succeed-NOP!' % (test, TEST_FILE_NAME, keyName)
    f = test_key.sync_upload_from_file(TEST_FILE_NAME)
    if (f):
        print ('\t%s: - FAILED') % test
    else:
        print ('\t%s: - Success') % test

    test = 'TEST-9'
    print '%s: Sync Download to %s from key=%s.  Should succeed-NOP' % (test, TEST_FILE_NAME, keyName)
    f = test_key.sync_download_to_file(TEST_FILE_NAME)
    if (f):
        print ('\t%s: - FAILED') % test
    else:
        print ('\t%s: - Success') % test

    fp = open ( TEST_FILE_NAME, 'wb' )
    fp.seek(0, os.SEEK_END)
    fp.write ( '0000000000000000000000000000000')
    fp.flush()
    fp.close()

    test = 'TEST-10'
    print '%s: Sync Upload %s to key=%s AFTER MODIFICATION  Should succeed!' % (test, TEST_FILE_NAME, keyName)
    f = test_key.sync_upload_from_file (TEST_FILE_NAME)
    if not f:
        print ('\t%s: - FAILED') % test
    else:
        print ('\t%s: - Success') % test

    fp = open ( TEST_FILE_NAME, 'wb' )
    fp.seek(0, os.SEEK_END)
    fp.write ( '11111111111111111111111111111111')
    fp.flush()
    fp.close()

    test = 'TEST-11'
    print '%s: Sync Download to %s from key=%s AFTER MODIFICATION  Should succeed!' % (test, TEST_FILE_NAME, keyName)
    f = test_key.sync_download_to_file (TEST_FILE_NAME)
    if not f:
        print ('\t%s: - FAILED') % test
    else:
        print ('\t%s: - Success') % test

    
    test = 'TEST-12'
    test_key = S3Util.AWS_Key(conn,bucket, 'boguskey')
    print '%s: Downloading key=%s to file=%s. Fails on not found!' % (test, key, TEST_FILE_NAME)
    try:
        test_key.get_object_to_file (TEST_FILE_NAME)
    except Exception, e:
        print '\t%s: - Success' % test
    else:
        print '\t%s: - FAILED' % test

    test = 'TEST-13'
    test_key = S3Util.AWS_Key(conn,bucket, keyName)
    print '%s: Dowload key=%s to file=%s.  Should succeed!' % (test, keyName, TEST_FILE_NAME)
    try:
        test_key.get_object_to_file (TEST_FILE_NAME)
    except Exception, e:
        print '\t%s: - FAILED! (%s)' % (test, e)
    else:
        print '\t%s: - Success!' % test

    test = 'TEST-14'
    print '%s: Deleting key=%s.  Should succeed!' % (test, keyName)
    try:
        test_key.delete_object ( )
    except Exception, e:
        print '\t%s: - FAILED! (%s)' % (test, e)
    else:
        print '\t%s: - Success!' % test

    test = 'TEST-15'
    print '%s: Deleting bucket=%s Should succeed!' % (test, bucket)
    try:
        AllBuckets.delete_bucket( bucket )
    except Exception, e:
        print '\t%s: - FAILED! (%s)' % (test, e)
    else:
        print '\t%s: - Success!' % test

        
    test = 'TEST-16'
    root_dir = TEST_DIR_ROOT
    bucket = u'AWSPyLib-testbucket-dirupload'
    print '%s: Recursively upload entire directory (%s) to %s' % (test, root_dir, bucket)
    try:
        AllBuckets.add_bucket ( bucket )
        test_bucket = S3Util.AWS_Bucket(conn, bucket)
        test_bucket.upload_dir ( root_dir )
        print 'UPLOADED DIRECTORY'
    except Exception, e:
        print '\t%s: - FAILED! (%s)' % (test, e)
    else:
        print '\t%s: - Success!' % test

    test = 'TEST-17'
    download_dir = 'DOWNLOAD-DIR'
    if (os.path.exists(download_dir) == False):
        os.mkdir(download_dir)
    print '%s: Download contents of bucket(%s) to %s' % (test, bucket, download_dir)
    try:
        test_bucket.download_dir ( download_dir )
    except Exception, e:
        print '\t%s: - FAILED! (%s)' % (test, e)
    else:
        print '\t%s: - Success!' % test
        
    Util.delete_directory(download_dir)
    os.remove(TEST_FILE_NAME)
    
    test = 'TEST-18'
    print '%s: Recursively delete all contents of bucket (%s)' % (test, bucket)
    try:
        AllBuckets.delete_bucket_recursive ( bucket )
    except Exception, e:
        print '\t%s: - FAILED! (%s)' % (test, e)
    else:
        print '\t%s: - Success!' % test        


def _perftest_(conn, test_bucket, test_file, test_file_size_in_bytes, count=1):
    
    test_key = S3Util.AWS_Key(conn,test_bucket.bucketName, test_file)
    
    import timeit
    
    my_clock = timeit.default_timer
        
    test_hdr = 'Starting upload of file=%s to %s(%s)' % (test_file, test_bucket.bucketName, test_key.keyName)
    print test_hdr
    try:
        start_time = my_clock( )
        for i in range (0,count):
            test_key.put_object_from_file ( test_file )
    except Exception, e:
        print 'Unable to upload file (%s) to bucket (%s)' % (test_file, test_bucket.bucketName)
    else:
        end_time = my_clock( )
        elapse_time = end_time - start_time
        speed = ( test_file_size_in_bytes * 8 * count / elapse_time ) / 1024
        print 'Uploaded file (%s) %d times in %f seconds. Upload speed=%f kbps\n' % (test_file,count,elapse_time,speed)
    
    
    local_file = 'download-file'
    test_hdr = 'Starting download of file=%s from %s(%s)' % (test_file, test_bucket.bucketName, test_key.keyName)
    print test_hdr
    try:
        start_time = my_clock()
        for i in range(0,count):
            test_key.get_object_to_file ( local_file )
    except Exception, e:
        print 'Unable to download file (%s) from bucket (%s)' % (test_file, test_bucket.bucketName)
    else:
        end_time = my_clock( )
        elapse_time = end_time - start_time
        speed = ( test_file_size_in_bytes * 8 * count / elapse_time ) / 1024
        print 'Downloaded file (%s)  %d times in %f seconds. Download speed=%f kbps\n' \
              % (test_file,count,elapse_time,speed)

    return


def perftest_s3( ):

    conn = S3Util.S3.AWSAuthConnection(Config.AWSProperties['AccessKey'], \
                                Config.AWSProperties['SecretKey'], ( Config.AWSProperties['SecureComm'] == True) )

    AllBuckets = S3Util.AWS_S3( AWSConnectionObject  = conn )

    perf_test_vector = [ 
        {'test_file':'10kb.file',  'test_file_size_in_bytes':1024*10,      'count':10},
        {'test_file':'100kb.file', 'test_file_size_in_bytes':1024*100,     'count':10},
        {'test_file':'1mb.file',   'test_file_size_in_bytes':1024*1024,    'count':1},
        {'test_file':'1mb.file',   'test_file_size_in_bytes':1024*1024,    'count':10},
#        {'test_file':'10mb.file',  'test_file_size_in_bytes':1024*1024*10, 'count':1}
    ]
            
    bucket_name = u'AWSPyLib-testbucket-perf-test'
    AllBuckets.add_bucket ( bucket_name )
    test_bucket = S3Util.AWS_Bucket(conn, bucket_name)
        
    for test in perf_test_vector:
        if (os.path.exists ( test['test_file'] ) == False ):
            Util.make_test_file( test['test_file'], test['test_file_size_in_bytes'] )
            
        _perftest_(conn, test_bucket, test['test_file'], test['test_file_size_in_bytes'], test['count'] )

    AllBuckets.delete_bucket_recursive( bucket_name )
    
    return

    
if __name__ == '__main__':
    
    test_s3()
    perftest_s3( )