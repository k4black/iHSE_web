/**
 * @fileoverview Admin page logic
 * File providing all functions which are used to control admin.html page
 * Including animations and http requests if that are sending by NOT nav elements
 */


//  https://github.com/ratiw/vuetable-2-tutorial/wiki/lesson-13
//  https://github.com/ratiw/vuetable-2-tutorial

Vue.use(Vuetable);
new Vue({
    el: '#app',
    components:{
        'vuetable-pagination': Vuetable.VuetablePagination
    },
    data: {
        fields: ['name', 'email','birthdate','nickname','gender','__slot:actions'],
        filterText: ''
    },
    computed:{
        /*httpOptions(){
        return {headers: {'Authorization': "my-token"}} //table props -> :http-options="httpOptions"
        },*/
    },
    methods: {
        onPaginationData (paginationData) {
            this.$refs.paginationTop.setPaginationData(paginationData);
            this.$refs.paginationInfoTop.setPaginationData(paginationData);
        },
        onChangePage (page) {
            this.$refs.vuetable.changePage(page)
        },
        editRow(rowData){
            alert("You clicked edit on"+ JSON.stringify(rowData))
        },
        deleteRow(rowData){
            alert("You clicked delete on"+ JSON.stringify(rowData))
        },

        doFilter () {
            console.log('doFilter:', this.filterText);
            alert("You doFilter"+ JSON.stringify(this.filterText))
        },
        resetFilter () {
            this.filterText = '';
            console.log('resetFilter');
            alert("resetFilter")
        }
    }
});

  //
  // export default {
  //   data () {
  //     return {
  //       filterText: ''
  //     }
  //   },
  //   methods: {
  //     doFilter () {
  //       console.log('doFilter:', this.filterText)
  //     },
  //     resetFilter () {
  //       this.filterText = ''
  //       console.log('resetFilter')
  //     }
  //   }
  // }


/** ===============  LOGIC and REQUESTS  =============== */


document.querySelector('.save').addEventListener('click', function () {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                alert('saved');
            }
        }
    };

    xhttp.open("GET", "http://ihse.tk:50000/admin_save", true);
    xhttp.withCredentials = true; // To send Cookie;
    xhttp.send();
});


document.querySelector('.update').addEventListener('click', function () {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                alert('updated');
            }
        }
    };

    xhttp.open("GET", "http://ihse.tk:50000/admin_update", true);
    xhttp.withCredentials = true; // To send Cookie;
    xhttp.send();
});


document.querySelector('.load').addEventListener('click', function () {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                alert('loaded');
            }
        }
    };

    xhttp.open("GET", "http://ihse.tk:50000/admin_load", true);
    xhttp.withCredentials = true; // To send Cookie;
    xhttp.send();
});


document.querySelector('.codes').addEventListener('click', function () {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                alert('created');
            }
        }
    };

    xhttp.open("GET", "http://ihse.tk:50000/admin_codes", true);
    xhttp.withCredentials = true; // To send Cookie;
    xhttp.send();
});

