package com.mysite.demo.MongoDB.Repository;

import com.mysite.demo.MongoDB.DataSchema.StaticInfo;
import java.util.Optional;

import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.data.mongodb.repository.Query;
import org.springframework.stereotype.Repository;
import java.util.List;



@Repository
public interface StaticInfoRepository extends MongoRepository<StaticInfo, String>{
}
