/*!

=========================================================
* Paper Dashboard React - v1.3.0
=========================================================

* Product Page: https://www.creative-tim.com/product/paper-dashboard-react
* Copyright 2021 Creative Tim (https://www.creative-tim.com)

* Licensed under MIT (https://github.com/creativetimofficial/paper-dashboard-react/blob/main/LICENSE.md)

* Coded by Creative Tim

=========================================================

* The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

*/
import React from "react";
import { useState,useEffect } from "react";
import { AsyncPaginate } from 'react-select-async-paginate';
import {base64encode, base64decode} from "nodejs-base64";
import useIsMounted from 'react-is-mounted-hook';
import * as Realm from "realm-web";
import Dropzone from 'react-dropzone';
import { TabContent, TabPane, Nav, NavItem, NavLink } from 'reactstrap';
import classnames from 'classnames';

import { GuardSpinner } from "react-spinners-kit";
import MonacoEditor from '@uiw/react-monacoeditor';

// reactstrap components
import {
  Button,
  Card,
  CardHeader,
  CardText,CardBody,
  CardTitle,
  FormGroup,
  Form,
  Input,
  Row,Label,FormText,
  Col,
  Modal, ModalFooter,
  ModalHeader, ModalBody
} from "reactstrap";

import TablePage from "views/Tables.js";





function User() {
  const axios = require('axios').default;
  const APP_ID = process.env.REACT_APP_APP_ID;
  const BASE_URL = process.env.REACT_APP_REALM_HOSTING_ROOT;
  const REALM_TOKENCHECK_ENDPOINT = process.env.REACT_APP_REALM_TOKENCHECK_ENDPOINT;
  const app = new Realm.getApp(APP_ID);



  // Modal open state
  const [modal, setModal] = React.useState(false);
  // Toggle for Modal
  const toggleModal = () =>{

    setWorking(true);

    setModal(!modal);

    setResultPublicIP("");
    setHasSuccess(false);
    setHasError(false);
    if(!modal){
      tryToSubmit();
    }
  };

  useEffect(() => {
    console.log('modal state changed!',modal);

    if(modal == true){
      console.log('modal open');
    }
    else{
      console.log('modal closed');
    }
  }, [modal]);


  // use same page for redirect
  if(window.location.search && String(window.location.search).includes("?redirect=1")){
    try{
      Realm.handleAuthRedirect();
      checkIfTokenIsValid();
    }catch(e){
      console.log('couldnt handle redirect from oauth',e);
    }
  }else{
    console.log('not a redirect from oauth');
  }
  const tryToLoginWithGoogle = async function(){

    try{
      // The redirect URI should be on the same domain as this app and
      // specified in the auth provider configuration.
      const credentials = Realm.Credentials.google(BASE_URL+"?redirect=1");
      // Calling logIn() opens a Facebook authentication screen in a new window.
      const realmUser = await app.logIn(credentials);
      // The logIn() promise will not resolve until you call `handleAuthRedirect()`
      // from the new window after the user has successfully authenticated.
      console.log('realmUser',realmUser);
      sessionStorage.setItem('_ru',base64encode((realmUser._accessToken)));
      sessionStorage.setItem('_rue',base64encode((realmUser._profile.data.email)));
      sessionStorage.setItem('_username',String(realmUser['_profile']['data']['email']).replace('@mongodb.com',''));
      let cprefix = String(sessionStorage.getItem('_username')+"-").replace(/[^a-z0-9]/gi,'');
      setClusterPrefix(cprefix);
      checkOnlineStatus();
    }catch(e){
      console.log('e',e);
    }

  };
  const checkIfTokenIsValid = function(){
    axios.post(
      REALM_TOKENCHECK_ENDPOINT,
      {token:String(base64decode(sessionStorage.getItem('_ru')))}
      ).then((res)=>{
        if(res.data && res.data.token_email !== ""){
          setLoginStatus(true);
        }else{
          setLoginStatus(false);
        }
      }).catch((e)=>{
        console.log('e',e.message)
        setLoginStatus(false);
      });

  };
  const [isLoggedIn,setLoginStatus] = useState(false);
  const [editorCode1,setEditorCode1] = useState("");
  const [editorCode2,setEditorCode2] = useState("");
  const [activeTab,setActive] = useState("2");

  const [clusterPrefix,setClusterPrefix] = useState("");

  const checkOnlineStatus = function(){

    if(sessionStorage.getItem('_ru')){
      checkIfTokenIsValid();
    }else{
      setLoginStatus(false);
    }

  };

  const tryToLogout = ()=>{
    sessionStorage.clear();
    window.location.reload(true);
  };

  const showFile1 = async (e) => {
    e.preventDefault()
    const reader = new FileReader()
    reader.onload = async (e) => {
      const text = (e.target.result)
      console.log(text)
      setEditorCode1(text);
    };
    reader.readAsText(e.target.files[0])
  };
  const showFile2 = async (e) => {
    e.preventDefault()
    const reader = new FileReader()
    reader.onload = async (e) => {
      const text = (e.target.result)
      console.log(text)
      setEditorCode2(text);
    };
    reader.readAsText(e.target.files[0])
  };



  async function loadOptionsA(search, loadedOptions) {
    return {options:[
      {"value":"us-east4-a","label":"us-east4-a"},
      {"value":"asia-east1-a","label":"asia-east1-a"},
      {"value":"asia-east2-a","label":"asia-east2-a"},
      {"value":"asia-northeast1-a","label":"asia-northeast1-a"},
      {"value":"asia-northeast2-a","label":"asia-northeast2-a"},
      {"value":"asia-northeast3-a","label":"asia-northeast3-a"},
      {"value":"asia-south1-a","label":"asia-south1-a"},
      {"value":"asia-south2-a","label":"asia-south2-a"},
      {"value":"asia-southeast1-a","label":"asia-southeast1-a"},
      {"value":"australia-southeast1-a","label":"australia-southeast1-a"},
      {"value":"europe-north1-a","label":"europe-north1-a"},
      {"value":"europe-west1-b","label":"europe-west1-b"},
      {"value":"europe-west2-b","label":"europe-west2-b"},
      {"value":"europe-west3-b","label":"europe-west3-b"},
      {"value":"europe-west4-b","label":"europe-west4-b"},
      {"value":"europe-west5-b","label":"europe-west5-b"},
      {"value":"europe-west6-b","label":"europe-west6-b"},
      {"value":"northamerica-northeast1-a","label":"northamerica-northeast1-a"},
      {"value":"southamerica-east1-a","label":"southamerica-east1-a"},
      {"value":"us-central1-a","label":"us-central1-a"},
      {"value":"us-east1-b","label":"us-east1-b"},
      {"value":"us-east4-a","label":"us-east4-a"},
      {"value":"us-west1-a","label":"us-west1-a"},
      {"value":"us-west2-a","label":"us-west2-a"},
      {"value":"us-west3-a","label":"us-west3-a"},
    ],hasMore:false};
  }

  const tryToSubmit = function(){
    var inputA = document.querySelector('input[name="fileA"]')
    var inputB = document.querySelector('input[name="fileB"]')

    setResultZone(input_zone.value);
    setResultName(input_clusterNm);

    var data = new FormData()
    data.append('fileA', inputA.files[0])
    data.append('fileB', inputB.files[0])
    data.append('clusterNm',clusterPrefix+input_clusterNm)
    data.append('zone',input_zone.value)
    data.append('ttl',input_ttl)
    data.append('maxRPS',input_maxRPS)
    data.append('currentRPS',input_currentRPS)
    data.append('username',sessionStorage.getItem('_username'))
    fetch('https://CHANGE_THIS_TO_YOUR_GOOGLE_CLOUD_RUN', {
      method: 'POST',
      body: data, mode: 'cors'
    }).then(r=>r.json()).then(data=>{
      console.log('data',data)

      if(data.success == "true"){
        let publicIP = data.public_ip[data.public_ip.length-1]
        var urlRegex = /(https?:\/\/[^ ]*)/;
        var url = String(publicIP).match(urlRegex)[1];
        url = String(url).split("<br"); //I absolutely hate this line
        url = url[0]; //and this one
        setResultPublicIP(url);
        setHasSuccess(true);
        setWorking(false);
      }else{
        setWorking(false);
        setHasError(true);
        setHasSuccess(false);
        setResultPublicIP(JSON.stringify(data));
      }
    });

  };



  const [input_clusterNm,setClusterNm] = useState("");
  const [input_zone,setZone] = useState("");
  const [input_ttl,setTTL] = useState(0);
  const [input_maxRPS,setMaxRPS] = useState(0);
  const [input_currentRPS,setCurrentRPS] = useState(0);

  const [result_public_ip,setResultPublicIP] = useState("");
  const [result_zone,setResultZone] = useState("");
  const [result_name,setResultName] = useState("");

  const [isWorking,setWorking] = useState(true);

  const [hasError,setHasError] = useState(false);
  const [hasSuccess,setHasSuccess] = useState(false);

  useEffect(() => {
    /*
    check auth status every 2 seconds
    */
    if(sessionStorage.getItem('_ru')){
      checkOnlineStatus();
    }
    const interval = setInterval(() => {
      console.log('checking...');
      checkOnlineStatus();
    }, 2000);

    return () => {
      console.log(`clearing interval`);
      clearInterval(interval);
    }
  }, [useIsMounted]);
  const toggle = function(tab) {
    if (activeTab !== tab) {
      setActive(tab);
    }
  };
  if(isLoggedIn){
    console.log('isLoggedIn',isLoggedIn)
  }
  return (
    <>

      <div className="content">
      <Modal isOpen={modal}
                modalTransition={{ timeout: 100 }}>
               <ModalHeader
                    toggle={toggleModal}>
                      MLocust -
                      {isWorking &&
                        <span>Working...</span>
                      }
                      {hasError &&
                        <span>Something went wrong</span>
                      }

                </ModalHeader>
                <ModalBody>
                  {isWorking &&
                    <div id="spinner-section">
                      <GuardSpinner size={150} />
                    </div>
                  }
                  {hasError &&
                    <div id="error-message-generic">
                      <p>Please try again. If this problem continues, contact us.</p>
                    </div>
                  }
                  <div id="modal-result">
                    <p>
                    <b>Cluster</b>:{result_name} @ {result_zone}
                    </p>
                    <hr />
                    {hasSuccess &&
                      <p>
                      <a href={result_public_ip}>{result_public_ip}</a>
                    </p>
                    }
                    {hasError &&
                      <p>
                      <span >{result_public_ip}</span>
                    </p>
                    }
                  </div>

                </ModalBody>
                <ModalFooter>
                    <Button color="primary" onClick={toggleModal}>Okay</Button>
                </ModalFooter>
            </Modal>
            {isLoggedIn ? ( <Button id="manage-clusters-btn" onClick={() => tryToLogout()}>LOGOUT</Button> ) : (<span></span>)}
      {isLoggedIn ? (
        <Row>
          <Col sm="12">

            <div id="mlocust-form-section">

            <div>
                <Nav tabs>

                  <NavItem>
                    <NavLink
                      className={classnames({ active: activeTab === '2' })}
                      onClick={() => { toggle('2'); }}
                    >
                      locust.py
                    </NavLink>
                  </NavItem>
                  <NavItem>
                    <NavLink
                      className={classnames({ active: activeTab === '3' })}
                      onClick={() => { toggle('3'); }}
                    >
                      requirements.txt
                    </NavLink>
                  </NavItem>
                  <NavItem>
                    <NavLink
                      className={classnames({ active: activeTab === '1' })}
                      onClick={() => { toggle('1'); }}
                    >
                      Configuration
                    </NavLink>
                  </NavItem>
                </Nav>
                <TabContent id="tabbd" activeTab={activeTab}>
                  <TabPane tabId="1">
                    <Row>
                      <Col sm="12">
                        <Card className="card-user">
                          <CardHeader>
                            <CardTitle tag="h5"></CardTitle>
                          </CardHeader>
                          <CardBody>
                              <Row>
                                <Col className="pr-1" md="11">
                                  <FormGroup>
                                    <label>Please select a region</label>
                                    <AsyncPaginate
                                        loadOptions={loadOptionsA}
                                        isClearable={true}

                                        value={input_zone}
                                        onChange={(e) => {setZone(e)}}/>
                                  </FormGroup>
                                </Col>
                              </Row>
                              <Row>
                                <Col className="pr-1" md="11">
                                  <FormGroup>
                                    <label>Please enter a name for the cluster</label>
                                    <Input
                                        type="text" placeholder="<cluster-name-goes-here>"
                                        value={input_clusterNm}
                                        onChange={(e) => {setClusterNm(e.target.value)}}/>
                                  </FormGroup>
                                </Col>
                              </Row>
                              <Row>
                                <Col className="pr-1" md="11">
                                  <FormGroup>
                                    <label>Please enter a TTL for the cluster</label>
                                    <Input type="number" placeholder="TTL in seconds goes here"
                                        value={input_ttl}
                                        onChange={(e) => {setTTL(e.target.value)}}/>
                                  </FormGroup>
                                </Col>
                              </Row>
                              <Row>
                                <Col className="pr-1" md="11">
                                  <FormGroup>
                                    <label>Please enter Est Max Ops/Sec for the cluster</label>
                                    <Input type="number" placeholder="Est Max Ops/Sec goes here"
                                        value={input_maxRPS}
                                        onChange={(e) => {setMaxRPS(e.target.value)}}/>
                                  </FormGroup>
                                </Col>
                              </Row>
                              <Row>
                                <Col className="pr-1" md="11">
                                  <FormGroup>
                                    <label>Please enter Immediate Ops/Sec for the cluster</label>
                                    <Input type="number" placeholder="Immediate Ops/Sec goes here"
                                        value={input_currentRPS}
                                        onChange={(e) => {setCurrentRPS(e.target.value)}}/>
                                  </FormGroup>
                                </Col>
                              </Row>

                              <Button color="success" onClick={()=>{
                                toggleModal();
                              }}>Submit</Button>
                              <Button id="rm-btn" color="danger" onClick={()=>{
                                let cprefix = String(sessionStorage.getItem('_username')+"-").replace(/[^a-z0-9]/gi,'');
                                setClusterPrefix(cprefix);
                                let url = 'https://mlocust-xddpmdzk4a-uc.a.run.app/rm_cluster?cluster='+encodeURIComponent(clusterPrefix+input_clusterNm)+"&zone="+encodeURIComponent(input_zone.value);
                                window.open(url, '_blank');
                              }}>RM</Button>
                            </CardBody>
                            </Card>
                      </Col>
                    </Row>
                  </TabPane>
                  <TabPane tabId="2">
                    <Row>
                      <Col sm="12">
                        <div>
                          <input type="file" name="fileA" onChange={(e) => showFile1(e)} />
                        </div>
                        <hr />
                        <div  className="me-wrap">
                          <MonacoEditor
                              language="python"
                              value={editorCode1}
                              options={{
                                theme: 'vs-dark',
                                readOnly: true,
                                automaticLayout: true
                              }}
                            />
                            <hr />
                          </div>
                      </Col>
                    </Row>
                  </TabPane>
                  <TabPane tabId="3">
                    <Row>
                        <Col sm="12">
                          <div>
                            <input type="file" name="fileB" onChange={(e) => showFile2(e)} />
                          </div>
                          <hr />
                          <div  className="me-wrap">
                            <MonacoEditor
                                language="python"
                                value={editorCode2}
                                options={{
                                  theme: 'vs-dark',
                                  readOnly: true,
                                  automaticLayout: true
                                }}
                              />
                              <hr />
                            </div>
                        </Col>
                      </Row>
                  </TabPane>
                </TabContent>
          </div>




        </div>

          </Col>
        </Row>
      ) : (
        <Row>
          <Col sm="12">
            <div>
                <p>You must be logged in to continue. <a id="login-link" href="#" onClick={()=>tryToLoginWithGoogle()}>Click here to login</a></p>
            </div>

          </Col>
        </Row>
      )}

      </div>
    </>
  );
}

export default User;
