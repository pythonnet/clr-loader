using System;

namespace example
{
    public class Class1
    {
    	public static int Test(IntPtr arg, int size) {
            Console.WriteLine($"Size {size}");
            return 0;
        }
    }
}
