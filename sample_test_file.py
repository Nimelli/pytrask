# test code find https://www.geeksforgeeks.org/python-program-for-print-number-series-without-using-any-loop/

# Python program to Print Number 
# series without using loop 
  
def PrintNumber(N, Original, K, flag): 
    #print the number 
    print(N, end = " ") 
      
    # change flag if number 
    # become negative 

    # @trask
    # todo: a test todo trask (one line description)
    # author: me

    """
    @trask
    doing:  implement comment block integration
            because it is useful for multiline integration
    author: me
    """

    # @trask
    # done: that was done

    # @trask
    # workaround: workaround for XXX
      
    if (N <= 0): 
        if(flag==0): 
            flag = 1
        else: 
            flag = 0
          
    # base condition for 
    # second_case (Adding K) 
      
    if (N == Original and (not(flag))): 
        return
      
    # if flag is true 
    # we subtract value until 
    # number is greater then zero 
      
    if (flag == True): 
        PrintNumber(N - K, Original, K, flag) 
        return
      
    # second case (Addition ) 
    if (not(flag)): 
        PrintNumber(N + K, Original, K, flag); 
        return
      
N = 20
K = 6
PrintNumber(N, N, K, True) 
  
# This code is contributed by Mohit Gupta_OMG 