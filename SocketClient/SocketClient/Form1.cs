using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Threading;
using System.Windows.Forms;
using Newtonsoft.Json;
using System.Windows.Forms;
using Quobject.SocketIoClientDotNet.Client;
using SocketIOClient;
using SocketClient;

namespace SocketClient
{
    public delegate void UpdateTextBoxMethod(string text);
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();
        }

        private void Form1_Load(object sender, EventArgs e)
        {

            var socket = IO.Socket("http://localhost:5000");

            socket.On(Socket.EVENT_CONNECT, ()=>
            {

            });
            socket.On("temp_check", (data) =>
            {
                           
                MessageBox.Show((string)data);

                // The socket.io server code looks like this:
                // socket.emit('hi', 'hi client');
            });
        }
            
    }
}
