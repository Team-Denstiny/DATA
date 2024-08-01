package com.mysite.demo.MongoDB;

import java.util.List;
import java.util.ArrayList;
import java.util.Optional;

import javax.sound.midi.MidiDevice.Info;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.mongodb.core.aggregation.ArithmeticOperators.Log;
import org.springframework.data.mongodb.core.aggregation.ArrayOperators.In;
import org.springframework.data.mongodb.core.query.Criteria;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.data.mongodb.core.query.Query;
import org.springframework.stereotype.Service;

import com.mysite.demo.MongoDB.DataSchema.StaticInfo;
import com.mysite.demo.MongoDB.DataSchema.DentCodeData;
import com.mysite.demo.MongoDB.DataSchema.DynamicInfoData;
import com.mysite.demo.MongoDB.DataSchema.TimeData;

import com.mysite.demo.MongoDB.Repository.DentCodeRepository;
import com.mysite.demo.MongoDB.Repository.DynamicInfoRepository;
import com.mysite.demo.MongoDB.Repository.StaticInfoRepository;

import groovyjarjarantlr4.v4.parse.ANTLRParser.delegateGrammar_return;

import org.bson.Document;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
@Service
public class UserService {
    private final StaticInfoRepository staticInfoRep;
    private final DentCodeRepository dentiCodeRep;
    private final DynamicInfoRepository dynamicInfoRep;

    private MongoTemplate mongoTemplate;

    @Autowired
    public UserService(StaticInfoRepository staticInfoRep,
                        DentCodeRepository dentiCodeRep,
                        DynamicInfoRepository dynamicInfoRep) {

        this.staticInfoRep = staticInfoRep;
        this.dynamicInfoRep = dynamicInfoRep;
        this.dentiCodeRep = dentiCodeRep;
    }
 
    public List<DentCodeData> getAllInfoData() {
        return dentiCodeRep.findAll();
    }

    
    public Optional<DentCodeData> getFindHospitalCode(String id) {
        try {
            return dentiCodeRep.findById(id);
        } catch (NumberFormatException e) {
            return Optional.empty();
        }
    }

    /* 
    public List<InfoData> getInfoDataByActreeNameKor(String name) {
        return infoRep.findByActreeId(this.actreeNameToCode(name));
    }
        */

}
